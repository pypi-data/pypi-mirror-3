from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.app.event-ploneintegration',
      version=version,
      description="Integration of plone.app.event into pre Plone 4.3 release.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone event',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://github.com/collective/plone.app.event-ploneintegration',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['plone','plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.event[archetypes]',
          'z3c.unconfigure',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """)
