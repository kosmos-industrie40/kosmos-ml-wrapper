# kosmos-mqtt-reaction

This Project is intended to provide a mqtt subscription trigger method for python projects.


# Overview
This project provides a python base class which implements the functionality
to handle MQTT communication for a custom analysis tool.
Its intended use is to wrap any analysis tool in the KOSMoS context where certain MQTT messages trigger said analysis tool. In turn, this tool may want to publish its analysis results to a predefined result MQTT topic e.g. to write results to a database or to trigger a successive workflow.

The ML Wrapper class listens to the trigger topic and publishes results to the correspnding result topic when deployed. This frees any ML engineer from having to deal with all overhead that comes with setting up the handling of MQTT messaging within the project.

The class needs to be configured through a configuration file (.ini) in which
expected request and answer topics as well as host and port of the desired MQTT broker need to be defined (see env_ml_wrapper.md for required configuration variables).

A child instance of this class will then be able to receive an MQTT message based on [KOSMoS MQTT standards](https://confluence.inovex.de/display/KOSMOS/MQTT) and pass the information to the registered analysis method and execute it in a separate thread.

Afterwards, the results of the analysis tool are itself parsed to conform to the required MQTT standards and publish a result message to the MQTT broker.

# Installation
You can install the ML Wrapper package from this repository directly:

    pip install git+https://gitlab.inovex.de/proj-kosmos/kosmos-mqtt-reaction.git
    

# How to use
After installing this package, you can use this package as described in examples/usage_example.py.

To test your application with the ML Wrapper, a testing framework to build on is provided in examples/test_example.py.

### Usage summary
*A slightly more conceptual description of the class*

As the run() method is an abstract method, it needs to be implemented to cover the needed ML analysis functionality.
Further customizations can be made for the methods retrieve_payload_data and resolve_payload_data to fit the need of the analysis tool.

The arguments of the run() method need to conform
to the outputs of retreive_payload_data() and to the inputs
of the resolve_payload_data() method.
The latter two can also be customized as needed.
(The current implementation takes the sensor or analysis data from an
incoming message, converts them to a pandas dataframe and passes this along with some more data from the payload to the run() method.)

In simplified terms, the main analysis workflow looks like the following:

    retrieved_data = self.retrieve_payload_data()
    result = self.run(*retrieved_data)
    message_payload = self.resolve_payload_data(result).

In the main program, self.start() shall be used to start an
infinite loop and react to incoming MQTT messages.

