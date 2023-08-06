from setuptools import setup, find_packages
import os

version = '1.3.2'

setup(name='collective.blogging',
      version=version,
      description="A blogging extension for Plone 4.x.",
      long_description=open(os.path.join("collective", "blogging", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Lukas Zdych',
      author_email='lukas.zdych@gmail.com',
      url='http://plone.org/products/collective.blogging',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.autoinclude',  # Required for Plone 3.2 compatibility
          'archetypes.schemaextender',
          'archetypes.markerfield',
          'plone.indexer',
          'plone.app.jquerytools',
          'Products.ATReferenceBrowserWidget',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
