import os
import codecs
from setuptools import setup

def read(fname):
    full_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), fname)
    if os.path.exists(full_path):
        return unicode(codecs.open(full_path).read())


setup(
    name = "setuptools_webdav",
    version = "0.0.1",
    author = "Marian Neagul",
    author_email = "marian@ieat.ro",
    description = "Setuptools/distribute plugin for uploading to webdav servers",
    license = "APL",
    keywords = "setuptools",
    url = "https://bitbucket.org/mneagul/setuptools-webdav",
    py_modules = ["setuptools_webdav"],
    long_description = read('README.rst'),
    classifiers = [
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Framework :: Setuptools Plugin",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        ],
    entry_points = {
        "distutils.commands": [
            "webdav_upload = setuptools_webdav:webdav_upload",
            ]
        },
    install_requires = ["Python_WebDAV_Library>=0.3.0"]
    )
