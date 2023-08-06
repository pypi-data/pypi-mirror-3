version = (0, 1, 7, 'stable')


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)
