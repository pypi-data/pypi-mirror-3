from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='d9t.gis',
      version=version,
      description="GIS Tools",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("d9t", "gis", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Daniel Kraft',
      author_email='dk@d9t.de',
      url='http://d9t.de/',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['d9t'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
