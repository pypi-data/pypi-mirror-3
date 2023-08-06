import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "mjsrpc2",
    version = "0.0.3",
    author = "Marian Neagul",
    author_email = "marian@ieat.ro",
    description = "mjsrpc2 is a extension of jsonrpc2 providing introspection and argument type validation",
    license = "APL",
    keywords = "jsonrpc2 rpc",
    url = "http://developers.mosaic-cloud.eu",
    package_dir = {'':"src/"},
    packages = ["mjsrpc2"],
    long_description = read('README.rst'),
    classifiers = [
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
    ],

    install_requires = ['jsonrpc2']
)
