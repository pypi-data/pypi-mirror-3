from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='scriptmutex',
      version=version,
      description="Create a mutex file for use in simple scripts",
      long_description="""\
This module is meant to provide a way to make sure that scripts don't end up running more than once. It creates a file with the pid of the process that created it and if the script is rerun while the previous instance is still running it will just gracefully die. If it detects the lockfile but the pid is no longer running then it will start the script and change the lockfile.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mutex filelock file lock',
      author='Adam Glenn',
      author_email='gekitsuu@gmail.com',
      url='https://github.com/gekitsuu/mutex',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
