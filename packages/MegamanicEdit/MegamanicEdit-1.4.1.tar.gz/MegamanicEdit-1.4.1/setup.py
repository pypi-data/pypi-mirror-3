from setuptools import setup, find_packages
import os

version = '1.4.1'

setup(name='MegamanicEdit',
      version=version,
      description="Batch and simplified editing of Archetypes",
      long_description=open(os.path.join("MegamanicEdit", "MegamanicEdit", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("MegamanicEdit", "MegamanicEdit", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['MegamanicEdit'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
