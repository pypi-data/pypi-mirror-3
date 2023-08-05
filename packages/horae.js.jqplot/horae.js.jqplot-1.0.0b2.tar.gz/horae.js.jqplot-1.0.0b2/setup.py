from setuptools import setup, find_packages
import os

version = '1.0.0b2'

setup(name='horae.js.jqplot',
      version=version,
      description="Provides the jqPlot jQuery plugin as fanstatic resources",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Simon Kaeser',
      author_email='skaeser@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['horae', 'horae.js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'fanstatic',
          'js.jquery',
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'fanstatic.libraries': [
              'horae.js.jqplot = horae.js.jqplot.resource:library',
          ]
      })
