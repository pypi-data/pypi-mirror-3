try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "clui",
    version = "1.0",
    author = "Luis Naranjo",
    author_email = "luisnaranjo733@hotmail.com",
    description = ("A customizable command line user interface."),
    license = "GNU GPL3",
    url = "https://github.com/doubledubba/clui",
    keywords = "CLUI clui ui command line user interface",
    #entry_points = {
    #'console_scripts': ['skel = skel:main']
    #},
    packages = ['clui'],
    platforms = 'any',
    install_requires = ['colorama==0.2.4'],
    #long_description=read('README.rst'), #TODO: FIX THIS
    #packages=['skeleton'],
    #include_package_data = True,
    #package_data = {
    #    'skeleton': ['docs','setup.py'],
    #}
)
