from setuptools import setup, find_packages

setup(name='WikiScout',
      packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests","*.scripts", "*.scripts.*", "scripts.*", "scripts"])
  )
