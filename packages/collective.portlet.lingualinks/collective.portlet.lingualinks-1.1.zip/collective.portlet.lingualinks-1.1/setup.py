from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.portlet.lingualinks',
      version=version,
      description="A portlet to provide links to translated content",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        ],
      keywords='plone multilingual linguaplone portlet',
      author='JeanMichel FRANCOIS',
      author_email='toutpt@gmail.com',
      url='https://github.com/collective/collective/collective.portlet.lingualinks',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.registry',
          'Products.LinguaPlone',
          # -*- Extra requirements: -*-
      ],
      extras_require = {'test': ['plone.app.testing',]},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
