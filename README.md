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

```
pip install git+https://gitlab.inovex.de/proj-kosmos/kosmos-mqtt-reaction.git
```
After the installation - assuming you are using a virtualenv `env` - you can execute 
```
env/bin/python env/lib/python3.7/site-packages/ml_wrapper/create_config_md.py
```
in your directory, to create the env_ml_wrapper.md file in your repository, if required.
    

# How to use
After installing this package, you can use this package as described in examples/usage_example.py.

To test your application with the ML Wrapper, a testing framework to build on is provided in examples/test_example.py.

## Usage summary
*A slightly more conceptual description of the class*

As the run() method is an abstract method, it needs to be implemented to cover the needed ML analysis functionality.
Further customizations can be made for the methods retrieve_payload_data and resolve_payload_data to fit the need of the analysis tool.

The arguments of the run() method need to conform
to the outputs of retrieve_payload_data() and to the inputs
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

## How to use in your project with gitlab CI CD
In order to be able to build your project, you will need to install this project via your requirements.txt

Locally that is no issue, but it gets a bit more tricky in the `.gitlab-ci.yml` Pipeline.

In order to set up your Pipeline properly, you will need to have a group deploy Token.
### Get your Group Deploy Token
#### Gopass
If you are not an owner of the proj-kosmos group in gitlab, you will need to use the
token that is saved in gopass. Simply use `gopass gitlab.inovex.de/deploytoken/gitlab-ci-token`
to retrieve the deploy token for this project.

#### Create a Gitlab Group Deploy Token
For this step you require ownership rights on the gitlab proj-kosmos group.
If you have a group token already, skip this step and go to the next heading.
- Go to https://gitlab.inovex.de/groups/proj-kosmos/-/settings/repository and click the
**Expand** Button besides `Deploy Tokens`.
- Enter a Name and the username `gitlab-ci-token`
- Click *Create deploy token*
- Copy and save the created token in your private password safe

### Set the token as Environment Variable for your pipeline
- Go to your project page (repository)
- In the menu on the left click on `Settings>CI/CD`
- Click the **Expand** Button next to **Variables**
- Click **Add Variable**
- As key enter `GIT_TOKEN`
- As value you enter the token you created / copied earlier
Repeat this step for the Username `GIT_USER` with value `gitlab-ci-token`

### Set up your gitlab pipeline
- Edit your .gitlab-ci.yml
- In every job, that needs to install / clone from another internal repository, 
enter the following two lines in the beginning.
```
- git config --global url."https://$GIT_USER:$GIT_TOKEN@gitlab.inovex.de".insteadOf https://gitlab.inovex.de
```
Then your pipeline before_script might look like this:
```
- before_script:
    - git config --global url."https://$GIT_USER:$GIT_TOKEN@gitlab.inovex.de".insteadOf https://gitlab.inovex.de
    - pip install -r requirements.txt
```