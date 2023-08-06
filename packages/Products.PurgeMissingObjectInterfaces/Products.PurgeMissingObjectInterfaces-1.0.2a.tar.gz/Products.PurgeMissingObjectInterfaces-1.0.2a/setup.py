from setuptools import setup, find_packages
import os

version = '1.0.2a'

setup(name='Products.PurgeMissingObjectInterfaces',
      version=version,
      description="A product for purging old and missing marker interfaces from objects",
      long_description=open(os.path.join("Products", "PurgeMissingObjectInterfaces", "readme.txt")).read() + \
          open(os.path.join("Products", "PurgeMissingObjectInterfaces", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: ZODB",
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Utilities",
        ],
      keywords='python zope interfaces plone silva developers',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'FakeZopeInterface',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
