from setuptools import setup, find_packages

name = 'zc.monitor'

long_description = (open('src/zc/monitor/README.txt').read() +
                    "\n\n" +
                    open('src/zc/monitor/CHANGES.txt').read())

setup(
    name = name,
    version = '0.3.1',
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
        'setuptools', 'zc.ngi', 'zope.component', 'zope.testing',
        ],
    include_package_data = True,
    zip_safe = False,
    )
