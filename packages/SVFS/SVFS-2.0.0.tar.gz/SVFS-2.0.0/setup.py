# SVFS's setup.py
from distutils.core import setup
setup(
    name = "SVFS",
    url = 'http://pypi.python.org/pypi?:action=display&name=SVFS',
    packages = [""],
    version = "2.0.0",
    description = "Multi-purpose virtual file system inside single file",
    author = "Andrew Stolberg",
    author_email = "andrewstolberg@gmail.com",
    keywords = ["filesystem", "archiving", "file-system"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems"
        ],
    long_description = """\
Simple Virtual File System v2 for Python 2
-------------------------------------

SVFS allows to create virtual filesystem inside file on real filesystem.
It can be used to store multiple files inside single file (with directory structure).
Unlike archives, SVFS allows to modify files in-place.
SVFS files use file-like interface, so they can be used (pretty much) like regular Python file objects.
Finally, it's implemented in pure python and doesn't use any 3rd party modules, so it should be very portable.
Tests show write speed to be around 10-12 MB/s and read speed to be around 26-28 MB/s.
"""
)
