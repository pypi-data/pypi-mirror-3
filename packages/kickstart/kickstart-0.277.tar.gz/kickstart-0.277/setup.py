from setuptools import setup, find_packages
import os

def find_package_data():
    """recursively build arbitrary files to be installed"""
    data = []

    for dirname, dirnames, files in os.walk('kickstart/templates/'):
        data.append('%s/*' % dirname)

    return data


setup(
    name = 'kickstart',
    scripts = ['kickstart.py'],
    include_package_data = True,
    packages = ['kickstart'],
    url = 'http://pypi.python.org/pypi/kickstart',
    version = '0.277',
    install_requires = ['PyYAML'],
    description = 'Framework agnostic setup script',
    author = 'Richard Layte',
    author_email = 'rich.layte@gmail.com'
)
