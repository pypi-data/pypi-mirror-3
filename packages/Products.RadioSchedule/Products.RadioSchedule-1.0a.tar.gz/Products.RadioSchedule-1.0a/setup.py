from setuptools import setup, find_packages
import os

version = '1.0a'

setup(name='Products.RadioSchedule',
      version=version,
      description="A content-type for storing information about radio show sending schedules",
      long_description=open(os.path.join("Products", "RadioSchedule", "readme.txt")).read() + '\n\n'+\
                       open(os.path.join("Products", "RadioSchedule", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='python plone content',
      author='Nidelven IT (Stig Rune Oeyra)',
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
