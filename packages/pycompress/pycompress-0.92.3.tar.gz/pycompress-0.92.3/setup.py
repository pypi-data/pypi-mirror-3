#!/usr/bin/env python

from distutils.core import setup, Extension
import os
from glob import glob


if os.name == 'posix':
    os.environ['CC'] = 'g++';
    os.environ['CXX'] = 'g++';
    os.environ['CPP'] = 'g++';
    os.environ['LDSHARED'] = 'g++'
else:
    print "setup script needs some love and care, if you are free, take some time, fix it up and give a pull request. Thanks. ;)"


setup(name='pycompress',
      version='0.92.3',
      description='Python binding for high compression ratio ZPAQ library',
      long_description="This library can achieve compression ratios like 10:1, which can be used for preprocessing logging, postprocessing backup and other textual data file",
      author='Anoop Thomas Mathew',
      author_email='atmb4u@gmail.com',
      url='http://www.bitbucket.org/atmb4u/pycompress',
      packages=['pycompress'],
      ext_modules=[Extension('pycompress/zpaq', ['zpaq.cpp'],
                        include_dirs = ['.'])],
      classifiers=[
                    'Development Status :: 3 - Alpha',
                    'Environment :: Console',
                    'Environment :: Web Environment',
                    'Intended Audience :: Developers',
                    'Intended Audience :: System Administrators',
                    'License :: OSI Approved :: BSD License',
                    'Operating System :: POSIX',
                    'Programming Language :: Python',
                    'Programming Language :: C++',
                    'Topic :: Utilities',
                    ],
     )

