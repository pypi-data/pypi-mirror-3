from setuptools import setup, find_packages
import os

version = open(os.path.join(
        'zest', 'emailhider', "version.txt")).read().strip()

setup(name='zest.emailhider',
      version=version,
      description=("A simple jQuery component for hiding email addresses from "
                   "spammers."),
      long_description=(
        open(os.path.join('zest', 'emailhider', "README.txt")).read()
        + "\n" +
        open("CHANGES.txt").read()),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zestsoftware email spamprotection javascript',
      author='Zest Software',
      author_email='s.hildebrandt@zestsoftware.nl',
      url='http://zestsoftware.nl',
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
      """,
      )
