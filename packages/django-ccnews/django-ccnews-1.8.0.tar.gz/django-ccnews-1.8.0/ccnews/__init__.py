version = (1, 8, 0)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)
