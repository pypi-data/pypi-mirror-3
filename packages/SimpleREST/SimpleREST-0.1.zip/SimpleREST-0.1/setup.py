'''
Created on 02.07.2012

@author: Jan Brohl <janbrohl@t-online.de>
@license: Simplified BSD License see license.txt
@copyright: Copyright (c) 2012, Jan Brohl <janbrohl@t-online.de>. All rights reserved.
'''
from distutils.core import setup
setup(name="SimpleREST",
      version="0.1",
      author="Jan Brohl",
      author_email="janbrohl@t-online.de",
      url="https://bitbucket.org/janbrohl/simplerest",
      packages=["simplerest"],
      package_dir={"":"src"},
      data_files=["license.txt"],
      license="Simplified BSD see license.txt",
      description="Use REST-APIs the easy way.",
      provides=["simplerest"])
