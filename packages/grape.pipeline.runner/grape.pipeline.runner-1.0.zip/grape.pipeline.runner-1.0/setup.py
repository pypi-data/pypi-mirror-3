import sys
from setuptools import setup, find_packages

install_requires = []

try:
    import argparse     # NOQA
except ImportError:
    install_requires.append('argparse')

with open("README.rst") as f:
    README = f.read()

with open("CHANGES.rst") as f:
    CHANGES = f.read()


setup(name='grape.pipeline.runner',
      version='1.0',
      packages=find_packages(),
      description=("Console script for running Grape RNA-Seq pipelines"),
      long_description=README + '\n' + CHANGES,
      author='Maik Roder',
      author_email='maikroeder@gmail.com',
      url='http://big.crg.cat/services/grape',
      license='GPL',
      include_package_data=True,
      zip_safe=False,
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: POSIX :: Linux',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: System :: Installation/Setup'],
      keywords='RNA-Seq pipeline ngs transcriptome bioinformatics',
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      grape-runner = grape.pipeline.runner:main
      """)
