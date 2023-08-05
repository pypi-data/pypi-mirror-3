from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.contentrules.mailfromfield',
      version=version,
      description="A Plone rules for send e-mail to addresses taken from the content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone rules mail plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='collective.contentrules.mailfromfield',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.contentrules',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
