# Matthew Henderson, 2012
# Created Wed Aug  8 15:37:51 BST 2012. Last updated Tue Aug 21 15:13:43 BST 2012

from distutils.core import setup

setup(
    name = 'ryser',
    version = '0.0.6',
    packages = ['ryser',],
    description = "Latin squares and related designs.",
    author = "Matthew Henderson",
    author_email = "matthew.james.henderson@gmail.com",
    scripts = ['bin/counterexample_investigation.py',
               'bin/hiltons_claim.py'],
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
    license = 'LICENSE.txt',
    long_description = open('README.rst').read(),
    install_requires=[
        "networkx >= 1.7.0",
        "vizing >= 0.0.11",
    ],
)

