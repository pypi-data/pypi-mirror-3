from setuptools import setup, find_packages
import os

version = '1.0.8'

setup(name='smitheme.bclear',
      version=version,
      description="Bethel's SMI Theme / Skin",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='python silva theme',
      author='Andy Altepeter / Bethel University',
      author_email='aaltepet@bethel.edu',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['smitheme'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'silva.core.layout',
          'silva.core.views',
          'silva.core.conf',
          'silva.core.smi',
          'silva.resourceinclude'
      ],
      )
