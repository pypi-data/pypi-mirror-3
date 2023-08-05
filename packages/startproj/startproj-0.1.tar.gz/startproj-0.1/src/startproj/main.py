from startproj import Template
from optparse import OptionParser, make_option, SUPPRESS_HELP
import os
import os.path
import shutil
import string
import tempfile
import textwrap


TEMPLATE_ROOT = os.path.expanduser('~/.startproj/templates')


def main():
    parser = OptionParser(usage='%prog template projectpath', option_list=(
        make_option('-c', '--create', action='store_true', default=False),
        make_option('-i', '--import', action='store_true', default=False, dest='import_template'),
        make_option('-d', '--debug', action='store_true', default=False, help=SUPPRESS_HELP),
    ))
    options, args = parser.parse_args()
    
    try:
        # startproj --import --create template
        if options.import_template and options.create:
            create_and_import_project(args, parser)
        
        # startproj --import template
        if options.import_template and not options.create:
            import_project(args, parser)
        
        # startproj --create template
        if not options.import_template and options.create:
            create_project(args, parser)
        
        # startproj template project
        if not options.import_template and not options.create:
            start_project(args, parser)
    
    except (KeyboardInterrupt, SystemExit,):
        raise
    except BaseException, e:
        if options.debug:
            raise
        else:
            print textwrap.fill('Error: %s' % (e,), width=78)
            exit(1)


def create_and_import_project(args, parser):
    template_name = template_from_args(args, parser)
    ensure_path(TEMPLATE_ROOT)
    template_path = os.path.join(TEMPLATE_ROOT, template_name)
    create_template(template_path)
    print 'Created template in "%s"' % (template_path,)


def import_project(args, parser):
    template_name = template_from_args(args, parser)
    ensure_path(TEMPLATE_ROOT)
    template_path = os.path.join(TEMPLATE_ROOT, template_name)
    shutil.copytree(template_name, template_path)
    print 'Copied template to "%s"' % (template_path,)


def create_project(args, parser):
    template_name = template_from_args(args, parser)
    create_template(template_name)
    print 'Created template "%s"' % (template_name,)


def start_project(args, parser):
    template_name, project_path = template_and_project_path_from_args(args, parser)
    template = Template.find(template_name, ('.', TEMPLATE_ROOT,))
    template.start_project(project_path)
    print 'Started project "%s"' % (os.path.basename(project_path),)


def ensure_path(path):
    try:
        os.makedirs(path)
    except (IOError, OSError,), e:
        if not os.path.isdir(path):
            raise


def create_template(path):
    os.mkdir(path)
    
    open(os.path.join(path, 'startprojconf.py'), 'w').write(textwrap.dedent('''
        """
        Hooks for startproj (http://www.github/nathforge/startproj)
        """
        
        
        # Called before a project is started.
        def before_start_project(template, **kwargs):
            pass
        
        
        # Called before any files are copied.
        def before_copy_files(template, **kwargs):
            pass
        
        
        # Called after all files have been copied.
        def after_copy_files(template, **kwargs):
            pass
        
        
        # Called before any of the copied files have been rendered
        # in the templating engine.
        def before_render_templates(template, **kwargs):
            pass
        
        
        # Called after all templates have been rendered.
        def before_render_templates(template, **kwargs):
            pass
        
        
        # Called after a project is started.
        def after_start_project(template, **kwargs):
            pass
    ''').strip())


def template_from_args(args, parser):
    if len(args) == 0:
        parser.error('Expected template name')
    elif len(args) == 1:
        return args[0]
    else:
        too_many_arguments(parser)


def template_and_project_path_from_args(args, parser):
    if len(args) == 0:
        parser.error('Expected template name')
    elif len(args) == 1:
        parser.error('Expected project_path')
    elif len(args) == 2:
        return args
    else:
        too_many_arguments(parser)


def too_many_arguments(count, parser):
    parser.error('Too many arguments')


if __name__ == '__main__':
    main()
