from setuptools import setup, find_packages
setup(
  name = 'periscope_django',
  version = '0.2',
  packages = find_packages(),
  author = "Harry Glaser, Tom O'Neill",
  author_email = "harry.glaser@gmail.com, tom.oneill@live.com",
  description = "Periscope is an analysis tool for production SQL databases. This module provides the API for Periscope to communicate with your Django app."
)
