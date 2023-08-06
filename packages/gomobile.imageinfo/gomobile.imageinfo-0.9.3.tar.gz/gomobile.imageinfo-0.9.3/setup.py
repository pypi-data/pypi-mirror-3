from setuptools import setup, find_packages
import os

version = '0.9.3'

setup(name='gomobile.imageinfo',
      version=version,
      description="Extract and manipulate different Zope image objects",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        ],
      keywords='zope image resize pil plone',
      author='mFabrik Rearch Oy',
      author_email='research@mfabrik.com',
      url='http://webandmobile.mfabrik.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gomobile'],
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
