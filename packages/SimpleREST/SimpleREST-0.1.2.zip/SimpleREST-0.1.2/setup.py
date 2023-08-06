'''
Created on 02.07.2012

@author: Jan Brohl <janbrohl@t-online.de>
@license: Simplified BSD License see license.txt
@copyright: Copyright (c) 2012, Jan Brohl <janbrohl@t-online.de>. All rights reserved.
'''
from distutils.core import setup

ver = "0.1.2"
name = "SimpleREST"
url = "https://bitbucket.org/janbrohl/" + name.lower()

setup(name=name,
      version=ver,
      author="Jan Brohl",
      author_email="janbrohl@t-online.de",
      url=url,
      download_url="%s/downloads/%s-%s.zip" % (url, name, ver),
      package_dir={"":"src"},
      data_files=["license.txt"],
      license="Simplified BSD see license.txt",
      provides=[name.lower()],

      packages=["simplerest"],
      description="Use REST-APIs the easy way."
      )
