from setuptools import setup, find_packages
import sys, os

here = os.path.dirname(__file__)

def _read(name):
    try:
        return open(os.path.join(here, name)).read()
    except:
        return ""

version = '0.1'
readme = _read("README.txt")

setup(name='standardenum',
      version=version,
      description="enum type",
      long_description=readme,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Topic :: Utilities",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Atsushi Odagiri',
      author_email='aodagx@gmail.com',
      url='https://bitbucket.org/aodag/standardenum',
      license='MIT',
      package_dir={"": "src"},
      packages=find_packages("src"),
      include_package_data=True,
      zip_safe=False,
      test_suite="standardenum",
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
