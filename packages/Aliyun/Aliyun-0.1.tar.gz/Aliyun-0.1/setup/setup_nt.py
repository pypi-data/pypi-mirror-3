# -*- coding: utf-8 -

def get_config():
    from setup_common import get_metadata

    metadata = get_metadata()
'''     
SCRIPTS = ['scripts/aliyun']
EXT_MODULES = [Extension(sources=['_aliyun.c'], **options)]

# Settings for M$ Windows
NT_INSTALL_REQUIRES = [
    'pyreadline>=1.7',
]

if name == 'nt':
    INSTALL_REQUIRES += NT_INSTALL_REQUIRES
    SCRIPTS = map(lambda x: '%s.bat' % (x), SCRIPTS)
    EXT_MODULES = []
'''

    return metadata
