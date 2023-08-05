"""
pdict is an implementation of a persistent dictionary using sqlite3 and json libraries. The library is silly and it sucks and as such it shouldn't be used by anyone. :)

Usage:
::
    >>> import pdicts
    
    >>> d = pdicts.PersistentDict("test.sqlite")
    
    >>> d['moto'] = "Let the beauty of what you love be what you do"
    
    >>> d['moto']  
    u'Let the beauty of what you love be what you do'

"""

from distutils.core import setup

setup(name = "pdicts",
    version="0.1",
    description="a persistent dictionary implementation",
    author="Peter Damoc",
    author_email="pdamoc@gmail.com",
    license="MIT",
    url="https://github.com/pdamoc/pdicts",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Database" ],
    py_modules=['pdicts'])
