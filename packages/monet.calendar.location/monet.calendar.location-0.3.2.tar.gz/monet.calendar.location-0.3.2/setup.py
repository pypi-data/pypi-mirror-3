from setuptools import setup, find_packages
import os

version = '0.3.2'

setup(name='monet.calendar.location',
      version=version,
      description="Add Italian features to monet.calendar.event",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.comune.modena.it/svn/monet/monet.calendar.location',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['monet', 'monet.calendar'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.MasterSelectWidget',
          'redturtle.entiterritoriali',
          'monet.calendar.event',
          'monet.calendar.extensions',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
