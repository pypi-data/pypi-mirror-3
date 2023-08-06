VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'micro': 0,
}


def get_version(short=False):
    """Get a string with app version.

    """
    version = "%(major)i.%(minor)i" % VERSION_INFO
    # append micro version only if not short and micro != 0
    if not short and VERSION_INFO['micro']:
        version = version + (".%(micro)i" % VERSION_INFO)

    return version


__version__ = get_version()
