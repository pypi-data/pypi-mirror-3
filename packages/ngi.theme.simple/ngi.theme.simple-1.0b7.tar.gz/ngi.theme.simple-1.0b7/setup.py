from setuptools import setup, find_packages
import os

version = '1.0b7'

setup(name='ngi.theme.simple',
      version=version,
      description="It is easy to setup the logo and footer using the control panel.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone Theme',
      author='Takashi NAGAI',
      author_email='nagai@ngi644.net',
      url='http://code.google.com/p/plone4-simpletheme/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ngi', 'ngi.theme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.registry',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
