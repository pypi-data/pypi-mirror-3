from setuptools import setup, find_packages
import os

version = '4.0.3b3'

setup(name='email_backport',
      version=version,
      description="A backport of the newest Python 2.x email module to >= Python 2.3",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Python License (CNRI Python License)",
        "License :: OSI Approved :: Python Software Foundation License"
        ],
      keywords='python email backport',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='Python Software Foundation License / Python License (CNRI Python License) and BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['email_backport'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
