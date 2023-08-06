from setuptools import setup, find_packages
from journaltocs import __version__ as version

setup(
    name="journaltocs", 
    version=version,
    description="A python wrapper for the JournalTOCs API (http://www.journaltocs.ac.uk/).",
    classifiers=[
        "Programming Language :: Python", 
        "Intended Audience :: Science/Research", 
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="JournalTOCs webservice",
    author="Simon Greenhill",
    author_email="simon@simon.net.nz",
    url="http://bitbucket.org/simongreenhill/journaltocsapi",
    license="BSD",
    packages=['journaltocs'],
    package_dir={'journaltocs': 'journaltocs'},
    package_data={},
    scripts=[],
)