from setuptools import setup, find_packages
import os

version = '1.0.4'

setup(name='Products.Undoer',
      version=version,
      description="A tool that enables rolling back (undoing) changes to a Zope Application database based on date and time.",
      long_description=open(os.path.join("Products", "Undoer", "readme.txt")).read() + "\n" +
                       open(os.path.join("Products", "Undoer", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        ],
      keywords='zope plone silva zmi undo rollback database',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='ZPL 2.1',
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
