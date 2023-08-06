from setuptools import setup, find_packages
import os

version = open('simplelayout/ui/dragndrop/version.txt').read().strip()

setup(name='simplelayout.ui.dragndrop',
      version=version,
      description="simplelayout drag and drop support",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Mathias Leimgruber (4teamwork)',
      author_email='m.leimgruber@4teamwork.ch',
      url='http://www.plone.org/products/simplelayout.ui.dragndrop',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['simplelayout', 'simplelayout.ui'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.js.jqueryui', 
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )



