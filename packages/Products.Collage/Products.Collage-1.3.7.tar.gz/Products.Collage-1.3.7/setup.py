# -*- coding: utf-8 -*-
# $Id$
import os
from setuptools import setup, find_packages

def _textOfModuleFile(filename):
    return open(filename, 'r').read().strip()

version = _textOfModuleFile(os.path.join('Products', 'Collage', 'version.txt'))

setup(name='Products.Collage',
      version=version,
      description=("A product to create page compositions in Plone."),
      long_description='\n\n'.join([
          _textOfModuleFile(name)
          for name in (
               'README.txt',
               os.path.join('docs', 'DEVELOPERS.txt'),
               os.path.join('docs', 'HISTORY.txt'))]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='plone layout composition',
      author='Malthe Borch',
      author_email='mborch@gmail.com',
      url='http://www.plone.org/products/collage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.Archetypes',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
