from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='py3o.renderclient',
      version=version,
      description="An easy solution to transform openoffice documents to supported formats",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='LibreOffice OpenOffice PDF',
      author='Florent Aide',
      author_email='florent.aide@gmail.com',
      url='',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['py3o'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'pyf.station',
          'pyjon.utils'
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite = 'nose.collector',
      )
