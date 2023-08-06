from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.ptg.contentleadimage',
      version=version,
      description="Display also contentleadimages",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        ],
      keywords='',
      author='Ales Zabala Alava (Shagi)',
      author_email='shagi@gisa-elkartea.org',
      url='http://github.com/collective/collective.plonetruegallery',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.ptg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.contentleadimage',
          'collective.plonetruegallery',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
