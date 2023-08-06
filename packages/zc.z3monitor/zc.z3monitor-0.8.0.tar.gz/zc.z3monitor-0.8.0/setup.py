from setuptools import setup, find_packages

name = 'zc.z3monitor'

long_description = (open('src/zc/z3monitor/README.txt').read() +
                    "\n\n" +
                    open('src/zc/z3monitor/CHANGES.txt').read())

setup(
    name = name,
    version = '0.8.0',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    license = 'ZPL 2.1',
    keywords = 'zope3',
    description=open('README.txt').read(),
    long_description=long_description,

    packages = find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = [
        'setuptools', 'zc.monitor', 'ZODB3', 'zope.component',
        'zope.publisher', 'zope.app.appsetup', 'zope.testing',
        'mock',
        ],
    include_package_data = True,
    zip_safe = False,
    )
