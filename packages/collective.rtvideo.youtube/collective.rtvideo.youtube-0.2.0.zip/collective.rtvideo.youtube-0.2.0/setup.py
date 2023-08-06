from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='collective.rtvideo.youtube',
      version=version,
      description="The YouTube Plone support for RedTurtle Video",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone plonegov video embed youtube',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/redturtle.video',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.rtvideo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'redturtle.video>=0.8.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
