from startproj.template import Template


VERSION = (0, 1)


def version_string():
    return '.'.join(str(component) for component in VERSION)
