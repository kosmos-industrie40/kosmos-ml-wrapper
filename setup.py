"""
This module sets up the package when it is installed
"""
import configparser
import setuptools
from ml_wrapper.create_config_md import create_config

# Read the Readme as long description
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

# Read the package config from the package_config.ini
CONFIG = configparser.ConfigParser()
CONFIG.read("package_config.ini")

# Author and Package
AUTHOR = CONFIG["author"]
PACKAGE = CONFIG["package"]

setuptools.setup(
    name=PACKAGE["name"],
    version=PACKAGE["version"],
    author=AUTHOR["name"],
    author_email=AUTHOR["email"],
    description=PACKAGE["description"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=PACKAGE["repository_url"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=PACKAGE["python_requires"],
)

create_config()
