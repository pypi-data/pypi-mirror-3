from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.lifecycle',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Simon Kaeser',
      author_email='skaeser@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['horae'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grok',
          'zope.principalannotation',
          # -*- Extra requirements: -*-
          'horae.auth',
          'horae.core',
          'horae.layout',
          'horae.timeaware',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
