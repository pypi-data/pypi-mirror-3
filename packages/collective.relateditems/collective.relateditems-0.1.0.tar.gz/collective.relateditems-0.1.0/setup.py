from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.relateditems',
      version=version,
      description="Backporting Plone 4 related items viewlet into Plone 3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        ],
      keywords='plone related-items backport viewlet',
      author='Luca Fabbri',
      author_email='luca@keul.it',
      url='http://plone.org/products/collective.relateditems',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone<4.0dev',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
