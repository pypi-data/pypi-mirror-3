from setuptools import setup, find_packages
import os

version = '1.2.6'

tests_require = ['zope.testing',
               'collective.testcaselayer']

setup(name='quintagroup.dropdownmenu',
      version=version,
      description="Multilevel portal dropdown menu for Plone sites.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web plone menu',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://quintagroup.com/services/plone-development/products/'
          'quintagroup.dropdownmenu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.registry',
          'plone.app.registry',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='quintagroup.dropdownmenu.tests',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
