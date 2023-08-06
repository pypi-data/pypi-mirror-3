#
# Copyright John Reid 2009, 2010, 2011, 2012
#

import os, infpy
from setuptools import setup


def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()



setup(
    name                   = "infpy",
    version                = infpy.__release__,
    author                 = "John Reid",
    author_email           = "john.reid@anti-spam.mrc-bsu.cam.ac.uk",
    description            = "A python inference library",
    license                = "BSD",
    # metadata for upload to PyPI
    keywords               = "Inference probabilistic models Gaussian processes Dirichlet processes",
    url                    = "http://sysbio.mrc-bsu.cam.ac.uk/johns/infpy/docs/build/html/",   # project home page, if any
    packages               = ['infpy.gp'], # doesn't seem to make any difference
    #py_modules             = ['infpy.gp'],
    data_files             = [('infpy', ['COPYRIGHT'])],
    install_requires       = ["numpy", "scipy", "matplotlib"],
    long_description       = read('README'),
    classifiers            = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

