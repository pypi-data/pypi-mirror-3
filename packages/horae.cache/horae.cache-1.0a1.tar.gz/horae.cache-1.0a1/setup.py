from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.cache',
      version=version,
      description="Provides utilities and decorators for caching",
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
      namespace_packages=['horae'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.memoize',
          'grok',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
