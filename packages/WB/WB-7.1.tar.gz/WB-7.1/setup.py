import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "WB",
    version = "7.1",
    author = "Luca Fini",
    author_email = "lfini@arcetri.astro.it",
    description = ("A CGI program to manage 'Billboards' where documents can be"
                   "posted (and edited and removed) through a simple WEB interface."),
    license = "GPL",
    keywords = "CGI CMS",
    scripts=['wb.py', 'wbmgmt.py'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Natural Language :: English",
        "Natural Language :: Italian",
        "Intended Audience :: System Administrators",
    ],
)
