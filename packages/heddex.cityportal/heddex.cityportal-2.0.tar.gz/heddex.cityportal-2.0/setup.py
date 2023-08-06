from setuptools import setup, find_packages
import os

version = '2.0'

setup(name='heddex.cityportal',
      version=version,
      description="Installable theme for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme skin heddex theo michael krishtopa',
      author='Michael Krishtopa',
      author_email='theo@heddex.biz',
      url='http://www.heddex.biz',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['heddex'],
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
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
