import os

from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '1.0.1'

tests_require = [
    'zope.testing',
    'zope.configuration',
    ],


setup(name='z3c.ptcompat',
      version=version,
      description="Zope-compatible page template engine based on Chameleon.",
      long_description=(
        ".. contents::\n\n" +
        read('README.txt')
        + "\n\n" +
        read("CHANGES.txt")
        ),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zpt template zope',
      url='http://pypi.python.org/pypi/z3c.ptcompat',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.pt >= 2.1',
          'zope.pagetemplate >= 3.6.2',
          'zope.traversing',
          ],
      extras_require=dict(
          test=tests_require,
      ),
      tests_require=tests_require,
      test_suite="z3c.ptcompat",
      )
