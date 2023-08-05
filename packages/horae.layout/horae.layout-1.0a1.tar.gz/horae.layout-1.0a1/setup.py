from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.layout',
      version=version,
      description="Provides the global layout for the Horae resource planning system",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Simon Kaeser',
      author_email='skaeser@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['horae'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grok',
          'fanstatic',
          'zope.fanstatic',
          # -*- Extra requirements: -*-
          'zc.relation',
          'js.jquery',
          'js.jqueryui',
          'BeautifulSoup',
          'grokcore.chameleon',
          'megrok.navigation',
          'megrok.pagetemplate',
          'megrok.form',
          'horae.core',
          'horae.datetime',
      ],
      entry_points={
          'fanstatic.libraries': [
              'horae.layout = horae.layout.resource:library',
          ]
      })
