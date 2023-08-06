from setuptools import setup, find_packages

try:
    description = file('README.txt').read()
except IOError:
    description = ''

version = "0.0"

setup(name='simpypi',
      version=version,
      description="Simple pypi package",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/mozilla/hg/simpypi',
      license="MPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',
         'FileServer'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
