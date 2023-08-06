# coding: utf-8
from distutils.core import setup, Extension
import sys

if sys.version_info < (2, 6):
    sys.stdout.write("At least Python 2.6 is required.\n")
    sys.exit(1)
    
setup(
    name = 'trminer',
    version = "1.1",
    author = 'Johannes Köster',
    author_email = 'johannes.koester@tu-dortmund.de',
    description = 'mine scientific publications for interesting sentences using patterns',
    license = 'MIT',
    package_dir = {'': 'lib'},
    package_data={'trminer': ['*.html']},
    packages = ['trminer'],
    scripts = ['trminer'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        #"Operating System :: POSIX",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
