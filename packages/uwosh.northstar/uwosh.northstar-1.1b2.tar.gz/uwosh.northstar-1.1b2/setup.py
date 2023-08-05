from setuptools import setup, find_packages
import os

version = '1.1b2'

setup(name='uwosh.northstar',
      version=version,
      description="Workflow management and application generation tool for Plone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='workflow uwosh plone manager ajax product generation',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='https://svn.it.uwosh.edu/svn/plone/Projects/uwosh.northstar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uwosh'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.jquerytools',
          'plone.app.workflowmanager'
          # -*- Extra requirements: -*-
      ],
      extras_require = { 'test': [
          'collective.testcaselayer',
          'Products.PloneTestCase'
      ]},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
