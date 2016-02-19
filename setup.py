#from setuptools import setup
from distutils.core import setup

setup(name='rmjet',
      author='Matt Bierbaum, Sam Kachuck, Alex Alemi',
      version='0.1',

      packages=['rmjet'],
      install_requires=[
          "numpy>=1.6.0",
          "matplotlib>=1.0.0",
          "pillow>=1.1.7",
      ],
)
