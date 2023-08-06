from setuptools import setup, find_packages
import os

version = '1.0b1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('docs', 'INSTALL.txt')
    + '\n' +
    read('docs', 'CONTRIBUTORS.txt')
    + '\n' +
    read('docs', 'CHANGES.txt')
    + '\n')

setup(name='collective.memberapproval',
      version=version,
      description="Member approval for Plone",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        ],
      keywords='plone pas user-management',
      author='Radim Novotny',
      author_email='novotny.radim@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFCore',
          'pas.plugins.memberapproval',
      ],
      extras_require = {
          'test': [
              'plone.app.testing',
              'interlude',
          ]
      },      
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
