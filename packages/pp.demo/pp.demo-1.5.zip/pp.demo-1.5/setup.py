from setuptools import setup, find_packages
import os

version = '1.5'

setup(name='pp.demo',
      version=version,
      description="pp.demo",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'loremipsum',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
