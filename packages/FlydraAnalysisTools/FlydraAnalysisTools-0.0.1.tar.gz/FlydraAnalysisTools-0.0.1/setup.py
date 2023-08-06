from setuptools import setup, find_packages
from distutils.core import Extension # actually monkey-patched by setuptools

setup(
    name='FlydraAnalysisTools',
    version='0.0.1',
    author='Floris van Breugel',
    author_email='floris@caltech.edu',
    packages=['flydra_analysis_tools'],
    url='http://pypi.python.org/pypi/FlydraAnalysisTools/',
    license='LICENSE.txt',
    description='Analysis scripts for analyzing and plotting flydra data',
    long_description=open('README.txt').read(),
)
