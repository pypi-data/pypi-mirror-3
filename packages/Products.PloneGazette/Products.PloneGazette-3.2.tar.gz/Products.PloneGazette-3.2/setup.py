import os
from setuptools import setup


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Plone',
    'Framework :: Plone :: 3.3',
    'Framework :: Plone :: 4.1',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Topic :: Communications :: Email'
]

version_file = os.path.join('Products', 'PloneGazette', 'version.txt')
version = open(version_file).read().strip()

readme_file= os.path.join('Products', 'PloneGazette', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('Products', 'PloneGazette', 'HISTORY.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.PloneGazette',
      version=version,
      author='Pilot Systems, Nidelven IT LTD and others',
      author_email='',
      maintainer='Morten W. Petersen',
      maintainer_email='info@nidelven-it.no',
      classifiers=CLASSIFIERS,
      keywords='Zope plone newsletter communication',
      url='http://plone.org/products/plonegazette',
      description='A complete Newsletter product for Plone.',
      long_description=long_description,
      packages=['Products', 'Products.PloneGazette'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools'],
      namespace_packages=['Products'],
      )
