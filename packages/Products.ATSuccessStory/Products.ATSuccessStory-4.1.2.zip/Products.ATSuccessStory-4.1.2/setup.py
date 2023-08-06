from setuptools import setup, find_packages
import os

version = '4.1.2'

setup(name='Products.ATSuccessStory',
      version=version,
      description="Success stories Product",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone 3.1 atsuccessstory',
      author='Franco Pellegrini',
      author_email='frapell@menttes.com',
      url='http://plone.org/products/atsuccessstory',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
