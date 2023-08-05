from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='wm.sampledata',
      version=version,
      description="UI and utility methods to generate sampledata for Plone projects",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone sampledata generation',
      author='Harald Friessnegger',
      author_email='harald (at) webmeisterei dot com',
      url='https://svn.plone.org/svn/collective/wm.sampledata/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
