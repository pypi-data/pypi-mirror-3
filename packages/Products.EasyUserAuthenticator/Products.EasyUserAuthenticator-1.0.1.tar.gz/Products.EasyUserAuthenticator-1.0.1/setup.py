from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='Products.EasyUserAuthenticator',
      version=version,
      description="Basic IMAP authentication plugin, suitable for customization towards other authentication backends",
      long_description=open(os.path.join("Products", "EasyUserAuthenticator", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "EasyUserAuthenticator", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='python zope pas authentication imap silva plone',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
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
