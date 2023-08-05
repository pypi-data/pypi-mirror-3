from startproj.util import copy_tree, rel_walk, matches_one
from collections import defaultdict
import inspect
import jinja2
import os.path
import re
import sys


class TemplateNotFound(Exception):
    pass


class Template(object):
    copy_include = [r'^.*$']
    copy_exclude = []
    copy_exclude_config = True
    template_filenames = [r'\.py$', r'\.txt$']
    
    NotFound = TemplateNotFound
    
    def __init__(self, path, config_module='startprojconf'):
        self.path = path
        self.config_module = config_module
        self.hooks = defaultdict(list)
        self.load_hooks()
        self.setup_renderer()
    
    @classmethod
    def find(cls, name, search_paths=(), **kwargs):
        for search_path in search_paths:
            path = os.path.join(search_path, name)
            if os.path.isdir(path):
                return Template(path, **kwargs)
        raise cls.NotFound('Template not found: %s' % (name,))
    
    def start_project(self, path):
        self.project_path = path
        self.call_hook('before_start_project')
        self.setup_renderer_for_project()
        self.copy_files()
        self.render_files()
        self.call_hook('after_start_project')
        del self.project_path
    
    def copy_files(self):
        self.call_hook('before_copy_files')
        copy_exclude = self.copy_exclude
        if self.copy_exclude_config:
            copy_exclude = copy_exclude + [r'^%s\.py[co]?$' % (re.escape(self.config_module),)]
        copy_tree(self.path, self.project_path, self.copy_include, copy_exclude)
        self.call_hook('after_copy_files')
    
    def render_files(self):
        self.call_hook('before_render_files')
        template_filenames = map(re.compile, self.template_filenames)
        for rel_path, dirnames, filenames in rel_walk(self.project_path):
            for filename in filenames:
                rel_filename = os.path.join(rel_path, filename)
                if matches_one(template_filenames, rel_filename.replace(os.path.sep, '/')):
                    self.render_file(rel_filename)
        self.call_hook('after_render_files')
    
    def render_file(self, filename):
        self.call_hook('before_render_file', filename=filename)
        full_filename = os.path.join(self.project_path, filename)
        template = self.renderer.from_string(open(full_filename).read())
        open(full_filename, 'wb').write(template.render())
        self.call_hook('after_render_file', filename=filename)
    
    def load_hooks(self):
        sys.path.insert(0, self.path)
        try:
            module = __import__(self.config_module, globals())
        except ImportError:
            if os.path.isfile(os.path.join(self.path, '%s.py' % (self.config_filename,))):
                raise
            else:
                return
        
        for name in dir(module):
            if name.startswith(('before_', 'after_',)):
                value = getattr(module, name)
                if callable(value):
                    if not inspect.getargspec(value)[2]:
                        raise ValueError('%s:%s must accept **kwargs' % (
                            self.config_module, name,
                        ))
                    self.hooks[name].append(value)
    
    def setup_renderer(self):
        self.renderer = jinja2.Environment(autoescape=False)
    
    def setup_renderer_for_project(self):
        self.renderer.globals = dict(
            project_path=self.project_path,
            project_name=os.path.basename(os.path.abspath(self.project_path)),
        )
    
    def call_hook(self, name, **kwargs):
        for hook in self.hooks[name]:
            hook(template=self, **kwargs)
    
    def config_filename(self):
        return '%s.py' % (self.config_module,)
