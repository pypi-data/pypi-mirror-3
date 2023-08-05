from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='valentine.multiparagraphpage',
      version=version,
      description="A page content type with multiple paragraphs(text bodies) without being folderish.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='archetype, plone, richtext, multi paragrah',
      author='Sasha Vincic',
      author_email='sasha dot vincic at valentinewebsystems dot se',
      url='http://svn.plone.org/svn/collective/valentine.multiparagraphpage/trunk/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['valentine'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'valentine.multiparagraphfield',
          'valentine.contentportlets',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
