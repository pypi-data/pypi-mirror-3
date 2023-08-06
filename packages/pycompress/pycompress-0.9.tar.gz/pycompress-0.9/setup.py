#!/usr/bin/env python

from distutils.core import setup, Extension
import os;


if os.name == 'posix':
    os.environ['CC'] = 'g++';
    os.environ['CXX'] = 'g++';
    os.environ['CPP'] = 'g++';
    os.environ['LDSHARED'] = 'g++'
else:
    print "setup script needs some love and care, if you are free, take some time, fix it up and give a pull request. Thanks. ;)"


setup(name='pycompress',
      version='0.9',
      description='Python binding for high compression ZPAQ library',
      author='Anoop Thomas Mathew',
      author_email='atmb4u@gmail.com',
      url='http://www.bitbucket.org/atmb4u/pycompress',
      packages=['pycompress'],
      ext_modules=[Extension('pycompress/zpaq', ['zpaq.cpp'])],

     )

