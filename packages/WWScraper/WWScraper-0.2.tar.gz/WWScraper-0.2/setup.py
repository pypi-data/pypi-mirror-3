#!/usr/bin/env python

from distutils.core import setup

setup(name='WWScraper',
      version='0.2',
      description='WeightWatchers eTools Site Scraper',
      author='Kurt Telep',
      author_email='ktelep@gmail.com',
      packages=['WWScraper'],
      requires=['BeautifulSoup', 'mechanize'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Utilities",
      ],
     )
