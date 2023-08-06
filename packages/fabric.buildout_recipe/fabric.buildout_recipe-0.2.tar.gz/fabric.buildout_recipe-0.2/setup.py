from setuptools import setup, find_packages
import os

version = '0.2'

here = os.path.abspath(os.path.dirname(__file__))
long_description = (
    open(os.path.join(here, 'README.txt')).read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open(os.path.join(here, 'CONTRIBUTORS.txt')).read()
    + '\n' +
    open(os.path.join(here, 'CHANGES.txt')).read()
    + '\n')

setup(name='fabric.buildout_recipe',
      version=version,
      description="Recipe base for writing fabric-buildout recipe.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Fabric Buildout Deploy',
      author='Imagawa Yakata',
      author_email='imagawa.yakata@gmail.com',
      url='https://bitbucket.org/imagawa_yakata/fabric.buildout-recipe',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['fabric'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          "fabric",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
