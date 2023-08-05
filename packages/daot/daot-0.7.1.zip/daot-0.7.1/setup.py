# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import codecs

setup(
  name = "daot",
  version = "0.7.1",
  packages = find_packages(),
##  scripts = ["say_hello.py"],

##  # Project uses reStructuredText, so ensure that the docutils get
##  # installed or upgraded on the target machine
##  install_requires = ["docutils>=0.3"],

  package_data = {
##      "": ["*.txt", "*.rst"] #,
      r"document\_build\html":["*.*"],
      r"document\zh":["*.rst", "*.html", "*.js"],
      r"document\en":["*.rst", "*.html", "*.js"]
  },

  author="Cao Xingming(Simeon.Chaos)",
  author_email="simeon.chaos@gmail.com",
  license="GPL",
  url="http://code.google.com/p/daot",
  download_url="http://code.google.com/p/daot",
  keywords = "dao dinpy lisp prolog dsl",

  description="the dao to programming",
)

long_description= codecs.open("readme", 'r', 'utf-8').read(),
    
platforms="Posix; MacOS X; Windows",

classifiers = [
               "License :: OSI Approved :: GNU General Public License (GPL)",
               "Natural Language :: Chinese (Simplified)",
               "Programming Language :: Python",
               "Topic :: Software Development :: Compilers",
               "Topic :: Text Processing :: General"]
