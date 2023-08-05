from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='valentine.multiparagraphfield',
      version=version,
      description="Field that handles multiple TextFields+RichWidgets as one field.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='archetypes, plone, atfield, kupu, richtext, richwidget, tinymce',
      author='Sasha Vincic',
      author_email='sasha dot vincic at valentinwebsystems dot com',
      url='http://svn.plone.org/svn/collective/valentine.multiparagraphfield/trunk/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['valentine'],
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
