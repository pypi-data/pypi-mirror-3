VERSION_INFO = {
    'major': 0,
    'minor': 1,
    'micro': 0,
    'sub': 'beta',
    'serial': 1
}


def get_version(short=False):
    """Concatenates ``VERSION_INFO`` to dotted version string."""
    assert len(VERSION_INFO) == 5
    assert VERSION_INFO['sub'] in ('alpha', 'beta', 'candidate', 'final')
    assert VERSION_INFO['serial'] >= 1
    assert isinstance(VERSION_INFO['major'], int)
    assert isinstance(VERSION_INFO['minor'], int)
    assert isinstance(VERSION_INFO['micro'], int)
    assert isinstance(VERSION_INFO['serial'], int)

    version = "%(major)s.%(minor)s" % VERSION_INFO
    if not short:
        # append micro version only if micro != 0
        if VERSION_INFO['micro']:
            version += ".%(micro)s" % VERSION_INFO
        # append sub (pre-release) version and number
        if VERSION_INFO['sub'] != 'final':
            version += "%(sub)s%(serial)s" % {
                'sub': VERSION_INFO['sub'][0],
                'serial': VERSION_INFO['serial'],
            }
    return version


__version__ = get_version()
