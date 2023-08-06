from setuptools import setup, find_packages
import os

version = '0.9.130'

setup(name='Products.IssueDealer',
      version=version,
      description="The Issue Dealer is an application for managing information. It is currently used by organizations and individuals to manage day-to-day tasks and information.",
      long_description=open(os.path.join("Products", "IssueDealer", "readme.txt")).read() +\
                       open(os.path.join("Products", "IssueDealer", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Bug Tracking",
        ],
      keywords='python zope2 cms',
      author='Morten W. Petersen',
      author_email='morphex@gmail.com',
      url='http://issuedealer.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.structuredtext',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
