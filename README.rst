ml_wrapper
==========

This Project is intended to provide a mqtt subscription trigger method
for python projects.

Quick-Start Tutorial
====================
Navigate/cd into your dev directory, where you keep all your projects.
Please pick your tools name first, because it is tideous to change afterwards.
Hence, fill in the fields encapsuled by < > in the following scripts.

**Please do these things in a standard terminal and not in the pycharm terminal.**

First setup your project (only if you haven't done that before)

::

    putup <test_tool>

Then use the provided template for a quickstart

::

    cookiecutter https://gitlab.inovex.de/proj-kosmos/libraries/python/ml_wrapper/ -f --directory templates

In the questions asked by cookiecutter, you will need to set the field project_name_in_src to <test_tool>.

If you don't have a virtual environment for you tool setup yet, it is now a good time to do so:

::

    cd <test_tool>
    python3.8 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install pytest pytest-cov
    python setup.py develop

You can now test your empty ml wrapper, using

::

    python setup.py.test


Last but not least:

- Open your project <test_tool> in charm and add an interpreter pointing towards your environment.
- Right click on src in the Project view and hit *Mark Directory as > Sources root*


Overview
========

This project provides a python base class which implements the
functionality to handle MQTT communication for a custom analysis tool.
Its intended use is to wrap any analysis tool in the KOSMoS context
where certain MQTT messages trigger said analysis tool. In turn, this
tool may want to publish its analysis results to a predefined result
MQTT topic e.g. to write results to a database or to trigger a
successive workflow.

The ML Wrapper class listens to the trigger topic and publishes results
to the corresponding result topic when deployed. This frees any ML
engineer from having to deal with all overhead that comes with setting
up the handling of MQTT messaging within the project.

The class needs to be configured through a configuration file (.ini) in
which expected request and answer topics as well as host and port of the
desired MQTT broker need to be defined (see env_ml_wrapper.md for
required configuration variables).

A child instance of this class will then be able to receive an MQTT
message based on `KOSMoS MQTT standards`_ and pass the information to
the registered analysis method and execute it in a separate thread.

Afterwards, the results of the analysis tool are itself parsed to
conform to the required MQTT standards and publish a result message to
the MQTT broker.

Installation
============

You can install the ML Wrapper package from this repository directly:

::

   pip install git+https://gitlab.inovex.de/proj-kosmos/libraries/python/ml_wrapper.git

After the installation - assuming you are using a virtualenv ``env`` -
you can execute

::

   env/bin/python env/lib/python3.7/site-packages/ml_wrapper/create_config_md.py

in your directory, to create the env_ml_wrapper.md file in your
repository, if required.

Runtime Requirements
====================

All the required variables that have to be set can be found in
`env_ml_wrapper.md`_. Especially the three variables

::

   CONFIG_MODEL_URL
   CONFIG_MODEL_TAG
   CONFIG_MODEL_FROM

are to be set per container/image because you will need to make sure
those are referring to your actual ml tool.

How to use
==========

After installing this package, you can use this package as described in
`usage_example.py`_.

To test your application with the ML Wrapper, a testing framework to
build on is provided in `test_example.py`_.

Using the template
------------------

The easiest way of getting started with this is by using the provided cookiecutter-template.
We assume that you have set up your project using pyscaffold's putup command. If you are only
starting, consider executing

::

    putup YOURPROJECTNAME --no-skeleton

If you are on the parent directory of YOURPROJECTNAME, simply execute the template by the followeing
code block. **Please be aware, that the following template will change files. So please make sure**
**to track everything with git before executing.**


::

    cookiecutter https://gitlab.inovex.de/proj-kosmos/libraries/python/ml_wrapper/ -f --directory templates

Make sure to enter the same value in the project_name_in_src field as in putup with YOURPROJECTNAME.

+------------------------------+----------------------------+-----------------------------------------+
| Variable to fill             | Default value              | Description/hint                        |
+==============================+============================+=========================================+
| src_folder_name              | src                        | Do not change                           |
+------------------------------+----------------------------+-----------------------------------------+
| test_folder_name             | tests                      | Do not change                           |
+------------------------------+----------------------------+-----------------------------------------+
| project_name_in_src          | simple_ml_tool             | Fill with the same                      |
|                              |                            | as in putup:                            |
|                              |                            | YOURPROJECTNAME                         |
+------------------------------+----------------------------+-----------------------------------------+
| short_project_description    | <None given>               |                                         |
+------------------------------+----------------------------+-----------------------------------------+
| ml_tool_name                 | simple_ml_tool             |  the python file name                   |
+------------------------------+----------------------------+-----------------------------------------+
| ml_class_name                | SimpleMlTool               | the Class of your tool                  |
+------------------------------+----------------------------+-----------------------------------------+
| result_type_of_the_tool      | time_series                | what you will return                    |
+------------------------------+----------------------------+-----------------------------------------+
| only_react_to_message_type   | I react to all messages    | the type of message you can handle      |
+------------------------------+----------------------------+-----------------------------------------+
| do_you_want_to_retrieve_data | no                         | do you want to retrieve additional data |
+------------------------------+----------------------------+-----------------------------------------+
| python_version               | 3.8                        |                                         |
+------------------------------+----------------------------+-----------------------------------------+
| build_python_package         | yes                        |                                         |
+------------------------------+----------------------------+-----------------------------------------+
| publish_docker_image         | yes                        |                                         |
+------------------------------+----------------------------+-----------------------------------------+
| build_docker_image           | yes                        |                                         |
+------------------------------+----------------------------+-----------------------------------------+


Usage summary
-------------

*A slightly more conceptual description of the class*

As the run() method is an abstract method, it needs to be implemented to
cover the needed ML analysis functionality. Further customizations can
be made for the methods retrieve_payload_data and resolve_payload_data
to fit the need of the analysis tool.

The standard information retrieved from the message (a DataFrame, a list
of DataFrames or a dictionary) will be available by the field
``out_message.in_message.retrieved_data``. More fields available are

::

   out_message.in_message.columns
   out_message.in_message.data
   out_message.in_message.metadata
   out_message.in_message.timestamp

These hold the original json message fields. The ``retrieved_data``
holds the information of the other fields in one of the three datatypes
DataFrame, list of DataFrames or dictionary, depending on the message
type that was received.

You can pass additional information from the retrieve_payload_data
function to the run method through the ``in_message``\ ’s field
``custom_information_field``. This will be available to the run method
via ``out_message.in_message.custom_information_field``.

The argument of the run() method is the prepared OutgoingMessage. This
OutgoingMessage holds the IncomingMessage in the field ``in_message``.
The run() method should calculate a DataFrame, a List of DataFrames or a
dictionary (representing the formal text analysis case of the
jsonschema) and return said calculation. The result will then be
transformed to the proper outputs in the retrieve_payload_data() method.
In case you need to change those values, you can overwrite the
retrieve_payload_data() method by setting the ``out_message``\ ’s field
``body`` directly. However, keep in mind that you will have to stick
to the `jsonschema`_ and provide a valid payload body.

In simplified terms, the main analysis workflow looks like the
following:

::

   in_message = self.retrieve_payload_data(in_message)
   out_message = Created by magic, but holds the in_message
   result = self.run(out_message)
   out_message = self.resolve_payload_data(result, out_message).

In the main program, self.start() shall be used to start an infinite
loop and react to incoming MQTT messages.

How to use in your project with gitlab CI CD
--------------------------------------------

In order to be able to build your project, you will need to install this
project via your requirements.txt

Locally that is no issue, but it gets a bit more tricky in the
``.gitlab-ci.yml`` Pipeline.

In order to set up your Pipeline properly, you will need to have a group
deploy Token. ### Get your Group Deploy Token #### Gopass If you are not
an owner of the proj-kosmos group in gitlab, you will need to use the
token that is saved in gopass. Simply use
``gopass gitlab.inovex.de/deploytoken/gitlab-ci-token`` to retrieve the
deploy token for this project. If that doesn’t work, you will have to
find the token in your correct gopass group.

Create a Gitlab Group Deploy Token
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this step you require ownership rights on the gitlab proj-kosmos
group. If you have a group token already, skip this step and go to the
next heading. - Go to
https://gitlab.inovex.de/groups/proj-kosmos/-/settings/repository and
click the **Expand** Button besides ``Deploy Tokens``. - Enter a Name
and the username ``gitlab-ci-token`` - Click *Create deploy token* -
Copy and save the created token in your private password safe

Set the token as Environment Variable for your pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Go to your project page (repository)
-  In the menu on the left click on ``Settings>CI/CD``
-  Click the **Expand** Button next to **Variables**
-  Click **Add Variable**
-  As key enter ``GIT_TOKEN``
-  As value you enter the token you created / copied earlier Repeat this
   step for the Username ``GIT_USER`` with value ``gitlab-ci-token``

Set up your gitlab pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Edit your .gitlab-ci.yml
-  In every job, that needs to install / clone from another internal
   repository, enter the following two lines in the beginning.

::

   - git config --global url."https://$GIT_USER:$GIT_TOKEN@gitlab.inovex.de".insteadOf https://gitlab.inovex.de

Then your pipeline before_script might look like this:

::

   - before_script:
       - git config --global url."https://$GIT_USER:$GIT_TOKEN@gitlab.inovex.de".insteadOf https://gitlab.inovex.de
       - pip install -r requirements.txt

Dockerfile
~~~~~~~~~~

If you are providing a docker build and push step, e.g. using kaniko,
then it’s recommended to provide the environment variables

::

   CONFIG_MODEL_URL
   CONFIG_MODEL_TAG
   CONFIG_MODEL_FROM

in your dockerfile via args and have them point to the same vars the
kaniko push will get the tag and the url from. The Dockerfile you are
writing will have to set the ENV variable ``CONFIG_MODEL_URL`` by the
ARG variable ``CONFIG_MODEL_URL``. The same goes for the other 2 ENV
Vars. Then you can pass them by setting

::

   --build-arg CONFIG_MODEL_URL=<yourURL> --build-arg CONFIG_MODEL_TAG=<yourTAG> --build-arg CONFIG_MODEL_FROM=<yourFROMID>

With docker this would then look something like

::

   docker build --build-arg CONFIG_MODEL_URL=<yourURL> --build-arg CONFIG_MODEL_TAG=<yourTAG> --build-arg CONFIG_MODEL_FROM=<yourFROMID> .

.. _jsonschema: src/ml_wrapper/kosmos_json_specifications/mqtt_payloads/analyses-formal.json
.. _KOSMoS MQTT standards: https://confluence.inovex.de/display/KOSMOS/MQTT-Specification
.. _env_ml_wrapper.md: src/env_ml_wrapper.md
.. _usage_example.py: src/examples/usage_example.py
.. _test_example.py: src/examples/test_example.py