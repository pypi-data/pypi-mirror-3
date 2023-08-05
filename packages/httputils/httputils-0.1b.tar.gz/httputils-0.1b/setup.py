import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "httputils",
    version = "0.1b",
    author = "Rizky Abdilah",
    author_email = "rizky.abdilah.mail@gmail.com",
    description = ("Simple python library used to wrap httplib function"),
    license = "GPL",
    keywords = "httputils, httplib",
    url = "http://packages.python.org/httputils",
    packages=['httputils'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
)
