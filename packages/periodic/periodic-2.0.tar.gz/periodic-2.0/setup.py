from setuptools import setup,find_packages
import os
def read(fname):
    return open(fname).read()
    
setup(
    name = "periodic",
    version = "2.0",
    author = "Jose Luis Naranjo Gomez",
    author_email = "luisnaranjo733@hotmail.com",
    description = ("A periodic table API."),
    license = "GNU GPL",
    keywords = "chem chemistry periodic table finder elements",
    url = "http://packages.python.org/periodic/",
    packages=['periodic'],
    long_description=''''See documentation here:

http://packages.python.org/periodic/''',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering"
    ],

)
