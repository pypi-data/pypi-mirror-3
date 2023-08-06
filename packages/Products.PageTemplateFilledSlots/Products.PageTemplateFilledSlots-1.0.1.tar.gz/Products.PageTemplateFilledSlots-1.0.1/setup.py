from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='Products.PageTemplateFilledSlots',
      version=version,
      description="Gives the template variable in page templates a method pt_filled_slots to see which slots are being filled",
      long_description=open(os.path.join("Products", "PageTemplateFilledSlots", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "PageTemplateFilledSlots", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2"
        ],
      keywords='python zope pagetemplates tal tales',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
