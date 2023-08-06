#!/usr/bin/env python
# coding: utf-8

# distutils stuff
from setuptools import setup, Extension

# utilities
import os, re, sys, contextlib

class CMake(object):
    SRC_DIR    = os.getcwd()
    BUILD_DIR  = os.path.join(SRC_DIR, 'build')
    CACHE_FILE = os.path.join(BUILD_DIR, 'CMakeCache.txt')
    NJOBS      = 2 
    _instances = {}
    
    def __init__(self, optimize=False, *args):
        self.optimize = optimize
        self.args     = args
        
    @classmethod
    def instance(cls, *args):
        if args not in cls._instances:
            cls._instances[args] = cls(*args)
        return cls._instances[args]
        
    @staticmethod
    @contextlib.contextmanager
    def _chdir(dirname=None):
        curdir = os.getcwd()
        try:
            if dirname is not None: os.chdir(dirname)
            yield
        finally:
            os.chdir(curdir)

    def _execute(self, action, command):
        with self._chdir(self.BUILD_DIR):
            print command
            err = os.system(command)
            if err != 0:
                sys.stderr.write( '%s: %s (err %d)\n' % (action, command, err,))
                sys.exit(-1)
            
    def configure(self, force=True):
        "Create makefiles"
        if not os.path.exists(self.BUILD_DIR):
            os.makedirs(self.BUILD_DIR)
        if not os.path.exists(self.CACHE_FILE) or force:
            self._execute("configure", self.cmake)

    def build(self, target):
        self.configure(force=False)
        self._execute("build", "%s %s" % (self.make, target))

    def install(self, force, *args):
        self.configure(force)
        self._execute("install", "%s %s install" % (self.make, " ".join(args)))

    def clean(self):
        if os.path.exists(self.BUILD_DIR):
            self._execute("clean", "%s clean" % self.make)
        self._execute("clean", "rm -r %s" % self.BUILD_DIR)
            
    @property
    def make(self):
        return "make -j %d" % self.NJOBS
        
    @property
    def cmake(self):
        return "cmake "                                          + \
            ' -DENABLE_GCC_OPTIMIZATION=%d '% int(self.optimize) + \
            ' '.join(self.args) + ' '                            + \
            self.SRC_DIR
        
# Build commands
from setuptools.command.build_ext import build_ext as _build_ext
class build_ext(_build_ext):
    def run (self):
        for ext in self.distribution.ext_modules:
            CMake.instance().build(ext.name)

# Install commands
from setuptools.command.install_lib import install_lib as _install_lib
class install_lib(_install_lib):
    def run(self):
        args = ["-DSITE_PACKAGE:PATH=%s" % os.path.abspath(self.install_dir)]
        CMake.instance(self.optimize, *args).install(True)

# clean and config
from distutils.command.clean  import clean as _clean
class clean(_clean):
    def run(self):
        CMake.instance().clean()

        
setup(name         = 'accountsSSO',
      version      = '0.0.5',
      author       = 'Carlos Martín',
      author_email = 'inean.es@gmail.com',
      url          = 'https://github.com/inean/python-accounts-sso',
      license      = 'LGPL2',
      description  = 'AccountSSO bindings for Harmattan platform',
      
      classifiers  = [
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
      ],

      cmdclass     = {
          'clean'       : clean,
          'build_ext'   : build_ext,
          'install_lib' : install_lib, 
      },
      
      ext_modules  = [
          Extension('Providers', ['dummy.cpp']),
          Extension('Accounts',  ['dummy.cpp']),
          Extension('SignOn',    ['dummy.cpp']),
      ]
  )
      

