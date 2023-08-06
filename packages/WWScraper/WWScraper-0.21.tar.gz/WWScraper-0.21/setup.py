#!/usr/bin/env python

from distutils.core import setup

setup(name='WWScraper',
      version='0.21',
      description='WeightWatchers eTools Site Scraper',
      author='Kurt Telep',
      author_email='ktelep@gmail.com',
      py_modules=['WWScraper'],
      requires=['BeautifulSoup', 'mechanize'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Utilities",
      ],
      data_files=[('example',['example/load_ww_db.py'])],
      url='http://http://pypi.python.org/pypi/WWScraper'
     )
