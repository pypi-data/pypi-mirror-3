from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup(name="thermos",
    version='0.1.5',
    description='Thermos Framework',
    long_description='A Django-like user-management system for Bottle',
    author='Paul Dwerryhouse',
    author_email='paul@dwerryhouse.com.au',
    url='http://leapster.org/software/thermos/',
    license='GPL',
    packages=['thermos','thermos.auth'],
    package_dir={'thermos': 'src/thermos'},
)
