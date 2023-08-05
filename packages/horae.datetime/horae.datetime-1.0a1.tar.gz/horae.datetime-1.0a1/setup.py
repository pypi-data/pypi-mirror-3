from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.datetime',
      version=version,
      description="zope.formlib datetime widget used by Horae",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Simon Kaeser',
      author_email='skaeser@raptus.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['horae'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'fanstatic',
          'zope.fanstatic',
          'js.jquery',
          'js.jqueryui',
      ],
      entry_points={
          'fanstatic.libraries': [
              'horae.datetime = horae.datetime.resource:library',
          ]
      })
