from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='MerlotTemplates',
      version=version,
      description="Paster templates for Merlot",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='grok merlot project management',
      author='Emanuel Sartor',
      author_email='emanuel@menttes.com',
      url='http://code.google.com/p/merlot/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['merlot'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Cheetah',
          'PasteScript'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      merlot_buildout = merlot.templates.merlot_buildout:MerlotBuildoutTemplate
      """,
      )
