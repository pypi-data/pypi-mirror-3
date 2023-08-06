from setuptools import setup, find_packages
import os

version = '1.8'

entry_points="""
[console_scripts]
migrator = collective.migrator.migrator:main

[zc.buildout]
mkdir      = collective.migrator.recipes.migrator:Mkdir
copy_file  = collective.migrator.recipes.migrator:CopyFile
export_obj = collective.migrator.recipes.migrator:ExportObject
import_obj = collective.migrator.recipes.migrator:ImportObject
del_object = collective.migrator.recipes.migrator:DelObject
ext_method = collective.migrator.recipes.migrator:ExternalMethod
submit_url = collective.migrator.recipes.migrator:SubmitUrl
pack_db = collective.migrator.recipes.migrator:PackDb
prepare_content = collective.migrator.recipes.migrator:PrepareContent
"""

setup(name='collective.migrator',
      version=version,
      description="Tool and buildout recipes for zope/plone content migration",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Buildout",
        ],
      keywords='buildout recipe zope plone content migration',
      author='Suresh V',
      author_email='suresh@grafware.com',
      url='http://plone.org/products/collective.migrator',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      test_suite = 'collective.migrator.tests',
      install_requires=[
          'setuptools',
      ],
      entry_points=entry_points,
      )
