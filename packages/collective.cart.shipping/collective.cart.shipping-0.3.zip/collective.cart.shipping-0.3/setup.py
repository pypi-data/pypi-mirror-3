from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('collective', 'cart', 'shipping', 'version.txt').strip()

long_description = (
    open("README.txt").read() + "\n" +
    open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
    open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
    open(os.path.join("docs", "CONTRIBUTORS.txt")).read() + "\n" +
    open(os.path.join("docs", "CREDITS.txt")).read()
    )

setup(name='collective.cart.shipping',
      version=version,
      description="Adds Shipping Methods to collective.cart.core.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Taito Horiuchi',
      author_email='taito.horiuchi@gmail.com',
      url='http://pypi.python.org/pypi/collective.cart.shipping',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.cart'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.cart.core',
          'hexagonit.testing',
          'mock',
          'pycountry',
          'setuptools',
          'unittest2',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
