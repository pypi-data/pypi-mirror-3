# Setup for zc.iso8601.

import os
import setuptools


here = os.path.dirname(os.path.abspath(__file__))

def read(path):
    return open(os.path.join(here, path)).read()

def long_description():
    return "\n\n".join([read("README.txt"),
                        read("CHANGES.txt")])


setuptools.setup(
    name="zc.iso8601",
    version="0.2.0",
    description="ISO 8601 utility functions",
    url="http://pypi.python.org/pypi/zc.iso8601/",
    long_description=long_description(),
    author="Fred Drake",
    author_email="fdrake@gmail.com",
    license="ZPL 2.1",
    classifiers=[
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        ],
    platforms="any",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    namespace_packages=["zc"],
    install_requires=[
        "pytz",
        "setuptools",
        "zope.testing",
        ],
    include_package_data=True,
    zip_safe=False,
    )
