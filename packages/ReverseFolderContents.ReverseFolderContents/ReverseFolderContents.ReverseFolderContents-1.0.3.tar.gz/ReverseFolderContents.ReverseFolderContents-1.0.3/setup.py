from setuptools import setup, find_packages
import os

version = '1.0.3'

setup(name='ReverseFolderContents.ReverseFolderContents',
      version=version,
      description="Enables reversing the listing of the folder contents in different views as well as in the navigation",
      long_description=open(os.path.join("ReverseFolderContents", "ReverseFolderContents", "readme.txt")).read() +\
                       open(os.path.join("ReverseFolderContents", "ReverseFolderContents", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent"
        ],
      keywords='python zope plone layout navigation monkeypatch archetypes',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d/',
      license='GPL 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ReverseFolderContents'],
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
