from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='quintagroup.portlet.cumulus',
      version=version,
      description="A tag cloud portlet that rotates tags in 3D using a Flash movie",
      long_description=open("README.txt").read() + "\n" +
          open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read(),                                            
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet flash tag cloud',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.portlet.cumulus',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.portlet'],
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
