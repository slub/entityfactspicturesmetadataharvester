"""
A commandline command (Python3 program) that reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves the (Wikimedia Commons file) metadata of these pictures (as line-delimited JSON records).
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='entityfactspicturesmetadataharvester',
      version='0.0.1',
      description='a commandline command (Python3 program) that reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves the (Wikimedia Commons file) metadata of these pictures (as line-delimited JSON records)',
      url='https://github.com/slub/entityfactspicturesmetadataharvester',
      author='Bo Ferri',
      author_email='zazi@smiy.org',
      license="Apache 2.0",
      packages=[
          'entityfactspicturesmetadataharvester',
      ],
      package_dir={'entityfactspicturesmetadataharvester': 'entityfactspicturesmetadataharvester'},
      install_requires=[
          'argparse>=1.4.0',
          'requests>=2.22.0',
          'rx>=3.0.1',
          'xmltodict>=0.12.0'
      ],
      entry_points={
          "console_scripts": ["entityfactspicturesmetadataharvester=entityfactspicturesmetadataharvester.entityfactspicturesmetadataharvester:run"]
      }
      )
