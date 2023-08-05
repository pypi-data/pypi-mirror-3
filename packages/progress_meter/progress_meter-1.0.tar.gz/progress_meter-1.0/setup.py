#!/usr/bin/env python

from distutils.core import setup

long_description = open("README.rst").read()

setup(name='progress_meter',
      version='1.0',
      description='A simple progress bar for long running tasks (Tkinter based)',
      author='Michael Lange, Thomas Kluyver',
      author_email='klappnase(at)freakmail(dot)de ; takowl(at)gmail(dot)com',
      url='https://bitbucket.org/takluyver/progress_meter',
      long_description=long_description,
      classifiers = ["License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python",
                     "Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 3",
                     "Topic :: Software Development :: User Interfaces",
                    ],
      py_modules=['progress_meter'],
     )
