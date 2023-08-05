from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='collective.flowplayer_toolbar',
      version=version,
      description="A Plone module which add an accessible Javascript controlsbar to collective.flowplayer",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: JavaScript",
        "Topic :: Multimedia :: Video",
        ],
      keywords='flowplayer javascript media player accessibility video',
      author='Keul',
      author_email='luca@keul.it',
      url='http://plone.org/products/collective.flowplayer_toolbar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          #'Plone',
          'collective.flowplayer>3.0dev',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
