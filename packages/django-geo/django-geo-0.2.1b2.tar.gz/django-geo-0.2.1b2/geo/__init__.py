NAME = 'django-geo'
VERSION = __version__ = (0, 2, 1, 'beta', 2)
__author__ = 'sax'

def get_version(version=None, short=False):
    """Derives a PEP386-compliant version number from VERSION."""
    if version is None:
        version = VERSION
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        sub = '.dev'
        if not short:
            import geo
            path =  geo.__path__[0]
            head_path = '%s/../.git/logs/HEAD' % path
            try:
                for line in open(head_path):pass
                revision = line.split()[0]
            except IOError:
                raise Exception('Aplha version is are only allowed as git clone')
            sub += revision

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub
