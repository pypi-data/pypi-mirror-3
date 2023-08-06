from setuptools import setup, find_packages
import os

version = '1.0.4'

setup(name='Products.PatchPloneContent',
      version=version,
      description="Various utilities to patch standard Plone content types",
      long_description=open(os.path.join("Products", "PatchPloneContent", "readme.txt")).read() + "\n" +
                       open(os.path.join("Products", "PatchPloneContent", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        ],
      keywords='python plone archetypes atcontenttypes monkeypatch',
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
