from setuptools import setup, find_packages
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name="Panacea",
      version="0.8.0",
      description="Declarative Mapper for SQLAlchemy (Forked from Elixir)",      
      author="Juan Manuel Garcia",
      author_email="jmg.utn@gmail.com",
      url="https://github.com/jmg/Panacea/",
      license = "MIT License",
      install_requires = [
          "SQLAlchemy >= 0.5.0"
      ],
      packages=find_packages(exclude=['ez_setup', 'tests', 'examples']),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Database :: Front-Ends",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      test_suite = 'nose.collector',
      **extra)
