import configparser
import setuptools

# Read the Readme as long description
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read the package config from the package_config.ini
cfg = configparser.ConfigParser()
cfg.read('package_config.ini')

# Author and Package
author = cfg["author"]
package = cfg["package"]

setuptools.setup(
    name=package['name'],
    version=package['version'],
    author=author['name'],
    author_email=author['email'],
    description=package['description'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=package['repository_url'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=package['python_requires']
)
