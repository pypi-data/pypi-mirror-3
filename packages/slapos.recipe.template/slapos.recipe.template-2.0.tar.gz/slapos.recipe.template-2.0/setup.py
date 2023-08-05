from setuptools import setup, find_packages
import os

version = '2.0'
name = 'slapos.recipe.template'
long_description = open("README.txt").read() + "\n" + \
    open(os.path.join('slapos', 'recipe',
                      'template', "README.txt")).read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

# extras_requires are not used because of
#   https://bugs.launchpad.net/zc.buildout/+bug/85604
setup(name=name,
      version=version,
      description="collective.recipe.template with network input support.",
      long_description=long_description,
      classifiers=[
          "Framework :: Buildout :: Recipe",
          "Programming Language :: Python",
        ],
      keywords='slapos recipe',
      license='GPLv3',
      namespace_packages=['slapos', 'slapos.recipe'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'setuptools', # namespaces
        'zc.buildout', # plays with buildout
        ],
      zip_safe=True,
      extras_require ={
        'test': 'zope.testing',
      },
      entry_points={
        'zc.buildout': [
          'default = slapos.recipe.template:Recipe',
      ]},
    )
