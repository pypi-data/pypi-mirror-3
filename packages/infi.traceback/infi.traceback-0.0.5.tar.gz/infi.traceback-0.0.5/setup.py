
SETUP_INFO = dict(
    name = 'infi.traceback',
    version = '0.0.5',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """better tracebacks""",
    long_description = """Tracebacks in Python are missing some useful debugging information, such is locals() in each stack frame
This module provides several mechanisms for better tracebacks:
* traceback_context. A context that in patches standard's library traceback module to print better tracebacks
* traceback_decorator. A decorator that calls the decorated method inside the traceback_context
* Nose Plugin. The plugin, enabled with '--with-infi-traceback', prints a better traceback for errors and failures""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'nose', 'mock', 'infi.pyutils'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [],
        'gui_scripts': [],
        'nose.plugins': ['infi.traceback = infi.traceback:NosePlugin', ],
        },
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

