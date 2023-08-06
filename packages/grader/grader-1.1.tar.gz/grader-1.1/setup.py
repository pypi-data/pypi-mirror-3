try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
    name = "grader",
    version = "1.1",
    author = "Jose Luis Naranjo Gomez",
    author_email = "luisnaranjo733@hotmail.com",
    description = ("A simple assignment completion checker."),
    license = "GNU GPL",
    install_requires= ['configobj',],
    entry_points = {
    'console_scripts': ['grade = grader.grader:grade']
    },
    package_data = {'': ['*.txt']},
    packages=['grader'],
    long_description=read('README'),
)
    
