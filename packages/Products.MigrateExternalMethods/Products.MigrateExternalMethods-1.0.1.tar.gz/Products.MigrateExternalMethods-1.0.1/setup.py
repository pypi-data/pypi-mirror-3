from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='Products.MigrateExternalMethods',
      version=version,
      description="A product that converts existing External Methods that used to live in the Extensions folder to a product folder",
      long_description=open(os.path.join("Products", "MigrateExternalMethods", "readme.txt")).read() + "\n" +
                       open(os.path.join("Products", "MigrateExternalMethods", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='python zope plone silva cmf migration developers',
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
