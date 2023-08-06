
SETUP_INFO = dict(
    name = 'infi.git_mirror',
    version = '0.0.4',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """short description here""",
    long_description = """long description here""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'gitpy', 'infi.execute', 'infi.pyutils'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['mirror_git_repository = infi.git_mirror.scripts:mirror_git_repository'],
        gui_scripts = []),
    )

platform_install_requires = {
    'windows' : [],
    'linux' : [],
    'macosx' : [],
}

def _get_os_name():
    import platform
    system = platform.system().lower().replace('-', '').replace('_', '')
    if system == 'darwin':
        return 'macosx'
    return system


def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    SETUP_INFO['install_requires'] += platform_install_requires[_get_os_name()]
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

