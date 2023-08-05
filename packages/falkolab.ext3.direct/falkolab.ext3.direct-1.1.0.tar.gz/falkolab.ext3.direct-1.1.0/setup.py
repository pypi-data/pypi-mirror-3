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
"""falkolab.ext3.direct

$Id$
"""
import sys, os
from setuptools import setup, find_packages
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
      name='falkolab.ext3.direct',
      version='1.1.0',
      author = 'Andrey Tkachenko',
      author_email = 'falko.lab@gmail.com',
      url='http://falkolab.ru/',
      license='ZPL 2.1',
      description='Zope3 Ext.Direct - Server-side Stack for ExtJS 3.',
      long_description = read('src', 'falkolab', 'ext3', 'direct', 'README.txt')
        + '\n\n' + read('CHANGES.txt'),
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['falkolab','falkolab.ext3'],
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
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
                'zope.app.securitypolicy',
                'simplejson',                  
                ]),
      install_requires=['setuptools',                        
                        'zope.interface',  
                        'zope.component',                       
                        'zope.schema',                        
                        'zope.security',
                        'zope.configuration',
                        'zope.publisher', 
                        'zope.app.folder',
                        'zope.app.cache',
                        'zope.app.appsetup',
                        'zope.app.pagetemplate', 
                        'zope.app.publication',                                           
                        'zope.viewlet',        
                        'zope.cachedescriptors',
                        'zope.traversing',
                        'zope.publisher',                                       
                        ],      
      include_package_data=True,
      zip_safe=False,
)