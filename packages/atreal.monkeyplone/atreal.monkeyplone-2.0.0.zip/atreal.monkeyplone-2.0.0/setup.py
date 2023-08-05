from setuptools import setup, find_packages
import os

version = '2.0.0'

setup(name='atreal.monkeyplone',
      version=version,
      description="A Patch for Plone cut/copy/paste/delete permissions",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='atReal',
      author_email='contact@atreal.net',
      url='http://www.atreal.net/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['atreal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher>=1.0b2',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
