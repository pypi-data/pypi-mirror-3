from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='gomobile.convergence',
      version=version,
      description="Multichannel content discrimination and overrides for Plone CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='mobile web cms plone zope applications apps iphone android',
      author='mFabrik Research Oy',
      author_email='research@mfabrik.com',
      url='http://webandmobile.mfabrik.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gomobile'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'gomobile.mobile',
          '',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-


      [z3c.autoinclude.plugin]
      target = plone        
      """,
      )
