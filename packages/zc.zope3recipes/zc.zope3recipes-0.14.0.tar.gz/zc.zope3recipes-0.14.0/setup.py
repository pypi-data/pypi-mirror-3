import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = "zc.zope3recipes"
setup(
    name = name,
    version = '0.14.0',
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for defining Zope 3 applications",
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://pypi.python.org/pypi/'+name,
    long_description = (
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('zc', 'zope3recipes', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    packages = find_packages('.'),
    include_package_data = True,
    namespace_packages = ['zc'],
    install_requires = [
        'zc.buildout >=1.2.0',
        'zope.testing',
        'setuptools',
        'zc.recipe.egg >=1.2.0',
        'ZConfig >=2.4a5'],
    entry_points = {
        'zc.buildout': [
             'application = %s.recipes:Application' % name,
             'app = %s.recipes:App' % name,
             'instance = %s.recipes:Instance' % name,
             'offline = %s.recipes:Offline' %name,
             ]
        },
    extras_require = dict(
        tests = ['zdaemon', 'zc.recipe.filestorage'],
        ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    )
