from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='collective.js.gritter',
      version=version,
      description="jQuery Gritter (Growl-like-notification) plugin for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='jquery plone notification growl',
      author='Radim Novotny',
      author_email='novotny.radim@gmail.com',
      url='http://pypi.python.org/pypi/collective.js.gritter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
