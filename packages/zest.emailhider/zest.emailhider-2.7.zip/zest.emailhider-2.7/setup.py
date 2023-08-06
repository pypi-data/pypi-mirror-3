from setuptools import setup, find_packages
import os

setup(name='zest.emailhider',
      version='2.7',
      description=("A simple jQuery component for hiding email addresses from "
                   "spammers."),
      long_description=(
        open("README.txt").read()
        + "\n" +
        open("CHANGES.rst").read()),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zestsoftware email spamprotection javascript',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='https://github.com/zestsoftware/zest.emailhider',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'jquery.pyproxy>=0.3.1'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
