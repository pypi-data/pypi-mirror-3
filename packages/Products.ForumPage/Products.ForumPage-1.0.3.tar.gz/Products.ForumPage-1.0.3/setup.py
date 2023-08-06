from setuptools import setup, find_packages
import os

version = '1.0.3'

setup(name='Products.ForumPage',
      version=version,
      description="A content-type that lists Ploneboard forums and their posts",
      long_description=open(os.path.join("Products", "ForumPage", "readme.txt")).read() + '\n\n' + \
                       open(os.path.join("Products", "ForumPage", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='python plone ploneboard presentation',
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
          'Products.Ploneboard',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
