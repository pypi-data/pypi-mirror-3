import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='markerlib',
      version='0.1',
      description='A compiler for PEP 345 environment markers.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        ],
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://bitbucket.org/dholth/markerlib/',
      keywords='packaging pep345',
      license='MIT',
      packages=['markerlib'],
      include_package_data=True,
      zip_safe=False,
      )

