from distutils.core import setup

setup(
    name = 'kickstart',
    scripts = ['kickstart.py'],
    url = 'http://pypi.python.org/pypi/kickstart',
    version = '0.14',
    requires = ['yaml'],
    description = 'Framework agnostic setup script',
    author = 'Richard Layte',
    author_email = 'rich.layte@gmail.com'
)
