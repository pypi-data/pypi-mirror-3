import codecs
from os import path
from setuptools import setup

try:
    unicode
except NameError:
    unicode = str


def read(name):
    full_path = path.join(path.abspath(path.dirname(__file__)), name)
    return unicode(codecs.open(full_path).read())

setup(
    name="setuptools_hg",
    version="0.4",
    author="Jannis Leidel",
    author_email="jannis@leidel.info",
    url="http://bitbucket.org/jezdez/setuptools_hg/",
    description="Setuptools/distribute plugin for finding files under Mercurial version control.",
    long_description=read("README.rst"),
    license="GPL2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Software Development :: Version Control",
        "Framework :: Setuptools Plugin",
    ],
    py_modules=["setuptools_hg"],
    entry_points={
        "setuptools.file_finders": [
            "hg = setuptools_hg:hg_file_finder"
        ]
    }
)
