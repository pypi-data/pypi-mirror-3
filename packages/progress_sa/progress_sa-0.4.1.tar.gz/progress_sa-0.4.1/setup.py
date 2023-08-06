# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

setup(name=u'progress_sa',
      version=version,
      description=u"Minimal SQLAlchemy dialect for OpenEdge 10/Progress.",
      long_description=u"""\
      A SQLAlchemy dialect that can be used to read OpenEdge 10 (aka
      Progress) databases over ODBC.

      This dialect was written to do some simple reporting only. It has
      not been tested with write operations.

      The Progress ODBC drivers come from DataDirect and return UTF-8
      by default or UCS-2. To work properly with these drivers, pyodbc
      needs to be compiled with the -fshort-wchar option and a small
      patch (included in the source distribution) that asks the DataDirect
      ODBC driver for UCS-2.
      """.encode("utf-8"),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Database :: Database Engines/Servers',
          ],
      keywords='sqlalchemy database dialect odbc',
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://bitbucket.org/dholth/progress_sa',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "SQLAlchemy >= 0.6.4",
      ],
      entry_points="""
      [sqlalchemy.dialects]
      progress = progress_sa:base.dialect
      """
      )
