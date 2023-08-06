version = (1, 6, 2,)

def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)

