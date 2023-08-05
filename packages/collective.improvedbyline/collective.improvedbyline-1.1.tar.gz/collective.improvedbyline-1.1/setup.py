from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.improvedbyline',
      version=version,
      description="Extends byline viewlet with Publication Date.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone viewlet byline publication date',
      author='Vitaliy Podoba',
      author_email='vitaliypodoba@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.improvedbyline',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
