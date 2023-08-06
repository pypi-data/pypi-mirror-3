#!/usr/bin/env python

import re
import setuptools

import vserver as module

setuptools.setup(
    name             = module.__name__,
    version          = module.__version__,
    description      = module.__doc__.partition('\n\n')[0],
    long_description = module.__doc__.partition('\n\n')[2],
    author           = module.__author__,
    author_email     = module.__author_email__,
    url              = module.__url__,
    py_modules       = [module.__name__],
    classifiers      = re.findall(r'\S[^\n]*', module.__classifiers__),
)
