from setuptools import setup, find_packages
import sys, os

version = '1.0.0'
shortdesc ="Products.GoPantsPockets"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='Products.GoPantsPockets',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Plone',
            'Operating System :: OS Independent',
            'Programming Language :: Python',           
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Georg Gogo BERNHARD',
      author_email='gogo@bluedynamics.com',
      url='',
      license='',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'Products.Relations',
      ],
      extras_require={
#      'py24': [
#          'uuid',
#      ],
      },
      )

