from setuptools import setup,find_packages
#from distutils.core import setup
import os

def read(fname):  # TODO: Implement this
    fpath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), fname)
    with open(fpath, 'r') as fhandle:
        return fhandle.read()
    
setup(
    name = "grader",
    version = '1.2',
    author = 'Jose Luis Naranjo Gomez',
    author_email = 'luisnaranjo733@hotmail.com',
    description = ("A homework checker for a 3d Modeling class"),
    license = "GNU GPL",
    #keywords = "chem chemistry periodic table finder elements",
    url = "https://github.com/doubledubba/grader",
    packages = ['grader'],
    #package_data = {'periodic': ['table.db']}
    include_package_data = True,
    entry_points = {
    'console_scripts': ['grader = grader.grader:main']
    },
    long_description=read('README.rst'),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Utilities",
    ],

)
