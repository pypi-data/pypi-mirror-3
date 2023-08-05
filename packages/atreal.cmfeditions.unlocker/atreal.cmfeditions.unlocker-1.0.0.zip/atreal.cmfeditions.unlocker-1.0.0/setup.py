from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='atreal.cmfeditions.unlocker',
      version=version,
      description="CMFEditions modifier that unlocks clone before saving",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone cmfeditions zope atreal externaleditor webdav',
      author='atReal',
      author_email='contact@atreal.net',
      url='http://www.atreal.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['atreal', 'atreal.cmfeditions'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
