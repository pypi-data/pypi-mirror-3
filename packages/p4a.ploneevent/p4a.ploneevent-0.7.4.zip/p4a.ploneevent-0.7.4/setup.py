from setuptools import setup, find_packages
import sys, os

version = '0.7.4'

f = open('README.txt')
readme = f.read()
f.close()

f = open('CHANGES.txt')
changes = f.read()
f.close()

setup(name='p4a.ploneevent',
      version=version,
      description="Plone4Artists event extensions for Plone",
      long_description=readme + '\n\n' + changes,
      classifiers=[
          'Framework :: Zope2',
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists recurring events calendar calendaring',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='http://pypi.python.org/pypi/p4a.ploneevent/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'python-dateutil',
          'archetypes.schemaextender',
          'dateable.kalends >= 0.3',
          'plone.app.locales > 3.3.5',
          'plone.indexer',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
