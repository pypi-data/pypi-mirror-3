from setuptools import setup, find_packages
import os

version = '0.2.6'

long_description = (
    open('CHANGES.txt').read()
    + '\n')

setup(name='bg.crawler',
      version=version,
      description='Crawler for importing data from a filesystem directory into Solr',
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Solr Python Fulltext Crawler',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/bg.crawler',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['bg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'argparse',
          'sunburnt',
          'httplib2',
          'python-magic',
          'chardet',
          'lxml',
          # -*- Extra requirements: -*-
      ],
      entry_points=dict(console_scripts=(
          'solr-crawler=bg.crawler.crawler:main',
          )),
      )
