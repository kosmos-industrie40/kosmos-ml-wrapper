# kosmos-mqtt-reaction

This Project is intended to provide a mqtt subscription trigger method for python projects.

## Setup for your project
Please follow instructions from [packaging.python.org](https://packaging.python.org/tutorials/packaging-projects/) 
for full instructions.

ToDos after cloning:
- Open package_config.ini and change values according to the package
- Open the LICENCE file and enter the licence text of your choice
- Open this README.md file and change it fitting to your actual package
- change the name of the folder `example_pkg` to a folder with your package name, e.g. `kosmos_fft_analysis`
- put your code into the new package folder 


## Generate distribution archives
This step is only required, if you want to publish your package to a index like the Python Packaging Index
- To create the archives you need the latest versions of `setuptools` and `wheel`
- `python3 setup.py sdist bdist_wheel` creates the distribution archives
