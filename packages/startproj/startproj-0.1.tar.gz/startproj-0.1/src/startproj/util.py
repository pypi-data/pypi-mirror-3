import os
import os.path
import re
import shutil


def matches_one(patterns, string):
    for pattern in patterns:
        if re.search(pattern, string):
            return True
    return False


def rel_walk(top, *args, **kwargs):
    for path, dirnames, filenames in os.walk(top, *args, **kwargs):
        assert path[:len(top)] == top
        rel_path = path[len(top):]
        yield (rel_path, dirnames, filenames,)


def copy_tree(from_path, to_path, include_patterns=(r'^.*$',), exclude_patterns=()):
    def include_file(filename):
        filename = filename.replace(os.path.sep, '/')
        return (
            matches_one(include_patterns, filename)
            and not matches_one(exclude_patterns, filename)
        )
    
    include_patterns = map(re.compile, include_patterns)
    exclude_patterns = map(re.compile, exclude_patterns)
    
    os.mkdir(to_path)
    for rel_path, dirnames, filenames in rel_walk(from_path):
        full_from_path = os.path.join(from_path, rel_path)
        full_to_path = os.path.join(to_path, rel_path)
        
        for index, dirname in enumerate(list(dirnames)):
            if include_file(os.path.join(rel_path, dirname)):
                os.mkdir(os.path.join(full_to_path, dirname))
            else:
                del dirnames[index]
        
        for filename in filenames:
            if include_file(os.path.join(rel_path, filename)):
                shutil.copyfile(
                    os.path.join(full_from_path, filename),
                    os.path.join(full_to_path, filename),
                )
