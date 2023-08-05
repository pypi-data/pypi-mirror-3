from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.flattr',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone flattr',
      author='Christoph Glaubitz',
      author_email='chris@chrigl.de',
      url='https://launchpad.net/collective.flattr/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'z3c.autoinclude',
          'zope.component',
          'zope.interface',
          'plone.app.registry',
          'archetypes.schemaextender',
          'z3c.form',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      extras_require = { 
          'test': [
              'plone.app.testing',
              'mocker',
          ]
      },
      )
