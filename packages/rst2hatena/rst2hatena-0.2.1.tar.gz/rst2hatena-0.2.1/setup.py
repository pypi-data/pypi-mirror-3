from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='rst2hatena',
      version=version,
      description="Convert reStructuredText to Hatena Diary syntax",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Topic :: Documentation",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Text Processing",
          "Topic :: Utilities",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='hatena restructuredtext',
      author='Yosuke Ikeda',
      author_email='alpha.echo.35@gmail.com',
      url='http://bitbucket.org/ae35/rst2hatena',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "docutils",
      ],
      entry_points={'console_scripts': ['rst2hatena = rst2hatena.rst2hatena:main']},
      test_suite="rst2hatena.tests"
)
