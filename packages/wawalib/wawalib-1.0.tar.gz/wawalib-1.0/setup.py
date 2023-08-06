from distutils.core import setup
from wawalib import wawa

setup(
    name = 'wawalib',
    packages = ['wawalib'],
    version = wawa.__version__,
    author = wawa.__author__,
    author_email = wawa.__author_email__,
    description = wawa.__doc__,
    url = 'http://pypi.python.org/pypi',
    keywords = ["wawa", "onlytiancai", "test"],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ]
)
