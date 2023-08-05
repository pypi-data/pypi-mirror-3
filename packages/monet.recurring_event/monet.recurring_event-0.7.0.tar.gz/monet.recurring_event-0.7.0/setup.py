# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

version = '0.7.0'

tests_require=['zope.testing']

setup(name='monet.recurring_event',
      version=version,
      description="Old event type for Plone (use only for remove older versions of this package)",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        "Programming Language :: Python",
        "Development Status :: 7 - Inactive",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.comune.modena.it/svn/monet/monet.recurring_event',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['monet', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'monet.calendar.event>=0.4.0',
                        #'p4a.plonecalendar>=2.0a5',
                        #'dateable.chronos',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'monet.recurring_event.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
