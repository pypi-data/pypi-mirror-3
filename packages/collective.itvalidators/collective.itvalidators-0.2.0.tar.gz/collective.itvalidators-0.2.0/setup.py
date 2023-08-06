from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='collective.itvalidators',
      version=version,
      description="A set of Archetype validators for Plone, some for Italian specific needs, others useful for all",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='plone archetype validator plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.itvalidators',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.validation',
      ],
      test_suite='collective.itvalidators.tests.test_validation.test_suite',
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
