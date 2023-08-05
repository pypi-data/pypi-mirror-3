VERSION = (0, 2, 1)

def version_string():
    return '.'.join(str(component) for component in VERSION)
