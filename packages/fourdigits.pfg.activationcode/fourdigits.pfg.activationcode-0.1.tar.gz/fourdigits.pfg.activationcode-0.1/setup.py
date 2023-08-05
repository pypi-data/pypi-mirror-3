from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='fourdigits.pfg.activationcode',
      version=version,
      description="A PFG field to provide a list of activation " + \
                  "codes and let PFG check them when submitting a form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='PFG Activation Code Field',
      author='Maarten Kling (Four Digits)',
      author_email='info@fourdigits.nl',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fourdigits', 'fourdigits.pfg'],
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
