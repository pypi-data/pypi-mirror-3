from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.recipe.symlink',
      version=version,
      description="A recipe to create symbolic links of an egg",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Matous Hora',
      author_email='matous.hora@dms4u.cz',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points = {'zc.buildout':
                    ['default = collective.recipe.symlink:Recipe']},
  )
