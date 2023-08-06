from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "ZODBFriendlyCounter", "version.txt")).read().strip()

setup(name='Products.ZODBFriendlyCounter',
      version=version,
      description="A counter which generates unique IDs and does so without bloating the ZODB",
      long_description=open(os.path.join("Products", "ZODBFriendlyCounter", "readme.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        ],
      keywords='python zope zodb counter zeo',
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
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
