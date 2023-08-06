#!/usr/bin/env python
 
from setuptools import setup
import pybiomaps

setup(name='PyBioMaps',
      version=pybiomaps.__version__,
      description='PyBioMaps is a framework to manage and visualize scientific data in a browser.',
      long_description='The server is based on bottle (python) and uses cairo to render 2d image tiles in realtime. On client-side a custom JavaScript library based on jQuery allows easy navigation through huge amounts of data with a google-maps-like interface.',
      author='Marcel Hellkamp',
      author_email='marc@gsites.de',
      url='http://example.com',
      packages='pybiomaps pybiomaps.plugins pybiomaps.render pybiomaps.resource'.split(),
      include_package_data=True,
      zip_safe = False,
      install_requires=['bottle >= 0.10',
                        'pycairo >= 1.8.6',
                        'biopython >= 1.5'],
      provides=['lucullus'],
      license='GPL',
      classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: No Input/Output (Daemon)',
		'Environment :: Web Environment',
		'Intended Audience :: Science/Research',
		'License :: Free for non-commercial use',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.6',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
		'Topic :: Multimedia :: Graphics :: Viewers',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'Topic :: Scientific/Engineering :: Visualization',
		'Topic :: Software Development :: Libraries :: Application Frameworks']
     )
