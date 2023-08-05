from setuptools import setup, find_packages
import os

version = '1.5'

setup(name='collective.portlet.similarcontent',
      version=version,
      description="A Plone portlet that uses the catalog internals to find 'similar' content to the page you are looking at",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone portlet similar related',
      author='Matt Hamilton',
      author_email='matth@netsight.co.uk',
      url='http://plone.org',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
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
      )
