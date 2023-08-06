import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup
setup(
  name="ordrin",
  version='0.1',
  packages=['ordrin', 'ordrindemo'],
  description="Ordr.in API Client",
  author="Ordr.in",
  author_email="tech@ordr.in",
  url="https://github.com/ordrin/api-py",
  install_requires=['requests>=0.13.1'],
  classifiers=[
    "Programming Language :: Python",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Development Status :: 4 - Beta",
    "Topic :: Software Development",
    "Topic :: Internet"],
  scripts=('ordrindemo/demo.py',))
