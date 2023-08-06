from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='FakeZopeInterface',
      version=version,
      description="A set of tools to build and import fake interface classes.  Usable when a Zope interface is missing from old or broken code",
      long_description=open(os.path.join("FakeZopeInterface", "FakeZopeInterface", "readme.txt")).read() +\
          open(os.path.join("FakeZopeInterface", "FakeZopeInterface", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: ZODB",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Utilities",
        ],
      keywords='python zope interfaces',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['FakeZopeInterface'],
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
