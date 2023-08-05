from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.topicitemsevent',
      version=version,
      description="Facilitate flexible scheduled notifications in Plone: Fire 'Topic Item Events' for items in a Topic",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone notifications',
      author='Kees Hink',
      author_email='hink@gw20e.com',
      url='http://plone.org/products/collective.topicitemsevent',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
      paster_plugins=["ZopeSkel"],
      )
