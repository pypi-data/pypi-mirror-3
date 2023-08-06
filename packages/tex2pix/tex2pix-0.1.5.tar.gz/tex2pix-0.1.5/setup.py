#! /usr/bin/env python

from distutils.core import setup

## Setup definition
import tex2pix
__doc__ = tex2pix.__doc__

setup(name = 'tex2pix',
      version = tex2pix.__version__,
      py_modules = ["tex2pix"],
      author = 'Andy Buckley',
      author_email = 'andy@insectnation.org',
      url = None,
      description = 'Lightweight renderer of LaTeX to a variety of graphics formats',
      long_description = __doc__,
      keywords = 'tex latex bibtex pdf eps postscript png graphics renderer',
      license = 'GPL',
      )
