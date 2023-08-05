##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
"""falkolab.ext3.layer

$Id$
"""
import sys, os
from setuptools import setup, find_packages
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

readme = read('src', 'falkolab', 'ext3', 'layer', 'README.txt')
changes = read('CHANGES.txt')

setup(
      name='falkolab.ext3.layer',
      version='1.0.1',
      author = 'Andrey Tkachenko',
      author_email = 'falko.lab@gmail.com',
      url='http://falkolab.ru/',
      license='ZPL 2.1',
      description='Zope3 UI Layer, resource and viewlets bundles for ExtJS v3 JavaScript library.',
      long_description = '\n\n'.join([readme, changes]),
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['falkolab','falkolab.ext3'],
      classifiers=[
                   'Development Status :: 3 - Alpha',
                   'Framework :: Zope3',
                   'Environment :: Web Environment',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: User Interfaces'],
      extras_require=dict(
          test=[
                'zope.testing',
                'zope.app.testing',
                ]),
      install_requires=['distribute',                        
                        'zope.interface', 
                        'zope.publisher', 
                        'zope.viewlet',                                           
                        'zope.contentprovider',            
                        ],      
      include_package_data=True,
      zip_safe=False,
)