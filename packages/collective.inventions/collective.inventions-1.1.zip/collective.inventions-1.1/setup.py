from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.inventions',
      version=version,
      description="A Diazo Skin for Plone 4",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone Diazo Skin Theme UI',
      author='Roberto Allende - Menttes SRL',
      author_email='rover@menttes.com',
      url='http://plone.org/products/xdvtheme.inventions',
      license='GPL V2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      paster_plugins=["ZopeSkel"],
      )
