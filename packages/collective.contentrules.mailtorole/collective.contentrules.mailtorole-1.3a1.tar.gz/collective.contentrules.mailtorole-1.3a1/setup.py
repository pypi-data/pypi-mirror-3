from setuptools import setup, find_packages
import os

version = open(os.path.join("collective", "contentrules", "mailtorole", "version.txt")).read().strip()

setup(name='collective.contentrules.mailtorole',
      version=version,
      description="Send e-mail to users having a role on the object",
      long_description=open("README.txt").read() + "\n" +
                      open(os.path.join("collective", "contentrules", "mailtorole", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone contentrules action mail',
      author='Zest Software (Fred van Dijk)',
      author_email='info@zestsoftware.nl',
      url='http://plone.org/products/collective.contentrules.mailtorole',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
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
