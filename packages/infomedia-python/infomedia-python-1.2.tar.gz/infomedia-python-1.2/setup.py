#!/usr/bin/env python

# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

import os.path, sys
import os

from setuptools import setup

version = '1.2'
version_files=(("src/infomedia/VERSION","%s\n"),)

setup(name='infomedia-python',
      version=version,
      description='Infomedia Python Utility Module',
      long_description="""
     A grab-bag of Python routines and frameworks that we have found
    helpful when developing GeCo toolkit.
""",
      maintainer="Infomedia Dev Group",
      maintainer_email="dev@infomedia.it",
      url="http://infomedia.it/dev",
      author='Emmanuele Somma',
      author_email='exedre@infomedia.it',
      license="GPL",
      package_dir = { '':'src' },
      packages= ["infomedia","infomedia.test",
                 "infomedia.hash2cfg","infomedia.hash2cfg.test" ],
      
#      doc_files=["GPL.txt", "CHANGES"],
#      unit_test_module=["infomedia.hash2cfg.test","infomedia.test"],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
)


for (filename, template) in version_files:
    filename = os.path.join(os.path.dirname(__file__), filename)
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        pass
    verfile = None
    try:
        verfile = open(filename, 'w')
        verfile.write(template % version)
        verfile.close()
    except:
        verfile.close()
        raise
