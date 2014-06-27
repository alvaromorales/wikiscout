from setuptools import setup, find_packages

setup(name='wikiscout',
      packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests","*.scripts", "*.scripts.*", "scripts.*", "scripts"])
  )
