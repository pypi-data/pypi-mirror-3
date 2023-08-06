# Matthew Henderson, 2012
# Created Wed Aug  8 15:37:51 BST 2012. Last updated Wed Aug  8 16:17:36 BST 2012

from distutils.core import setup

setup(
    name = 'ryser',
    version = '0.0.3',
    packages = ['ryser',],
    description = "Latin squares and related designs.",
    author = "Matthew Henderson",
    author_email = "matthew.james.henderson@gmail.com",
    url = "http://packages.python.org/ryser/",
    download_url = "http://pypi.python.org/pypi/ryser/",
    keywords = [""],
    classifiers = [
        "Programming Language :: Python",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    license = ' Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License',
    long_description = open('README.txt').read(),
)

