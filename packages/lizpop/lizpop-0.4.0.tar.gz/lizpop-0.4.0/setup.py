#-*- coding: utf-8 -*-
from distutils.core import setup

def read(fname):
  import os
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = 'lizpop',
  packages = ['lizpop'],
  version = '0.4.0',
  description = 'Scheme interpreter in Python',
  long_description = read('README.txt'),
  author='Tetsu Takaishi',
  author_email='te2fm.t@gmail.com',
  url='http://pypi.python.org/pypi/lizpop/',
  license='BSD',
  classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers', 
    # 'Operating System :: OS Independent',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Lisp',
    'Programming Language :: Scheme',
    'Programming Language :: Python :: 2',
    'Topic :: Software Development :: Interpreters',
    ],

  #data_files=[('',['lizpop/boot.scm'])],
  package_data = {'lizpop':['boot.scm']},
)
