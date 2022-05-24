# Quickstart

## Prerequisites
### 1. Configured MQTT Broker

The ML Wrapper class listens to the trigger topic and publishes results
to the corresponding result topic when deployed. This frees any ML
engineer from having to deal with all overhead that comes with setting
up the handling of MQTT messaging within the project. Therefore an **MQTT Broker** needs to be configured.

One way to do this is with the [Eclipse Mosquitto](https://mosquitto.org/) Broker.

After installing Mosquitto you can start the broker on port 1883 with:

``` 
mosquitto -p 1883 
```

Then you subscribe to the broker (In a seperate Terminal) with: 

```
mosquitto_sub -t '#' -h 0.0.0.0
```

You will receive every MQTT Message from every Topic. To subscribe to a specific topic, replace `'#'` with the specific topic.


## Simple Usecase

We will use an [Example Analysis Tool](https://github.com/kosmos-industrie40/kosmos-ml-wrapper/blob/master/src/examples/usage_example.py). It listens to Messages to the topic `kosmos/analytics/model-test/tag-test`. When it gets a message on this topic it will return  an dict with the key `ind` containing the list [0,1,2,3,4,5,6,7,8,9] on the topic `kosmos/analyses/abc`

After inspecting [example.py](hhttps://github.com/kosmos-industrie40/kosmos-ml-wrapper/blob/master/src/examples/usage_example.py) you can then start the Analysis Tool with: 

```python
python example.py
```
To send a MQTT Message to the topic `kosmos/analytics/model-test/tag-test` you can use following command:

You can inspect the [Example Json Files](https://github.com/kosmos-industrie40/kosmos-ml-wrapper/blob/master/src/ml_wrapper/messaging/json_handling/kosmos_json_specifications/mqtt_payloads/ml-trigger/analysis-example.json) - if needed. 

```
 mosquitto_pub -t "kosmos/analytics/model-test/tag-test" -h 0.0.0.0 -p 1883 -f src/ml_wrapper/messaging/json_handling/kosmos_json_specifications/mqtt_payloads/ml-trigger/analysis-example.json 
```

The client will get following Message:

```json
{
   "body":{
      "type":"time_series",
      "from":"test",
      "model":{
         "url":"test",
         "tag":"test"
      },
      "calculated":{
         "message":{
            "machine":"mach",
            "sensor":"abc"
         },
         "received":"2022-05-09T10:28:19.236046+00:00"
      },
      "results":{
         "data":[
            [
               "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]"
            ]
         ],
         "columns":[
            {
               "name":"ind",
               "type":"string"
            }
         ]
      },
      "timestamp":"2022-05-09T10:28:19.311987+00:00"
   },
   "signature":"This has to be done"
}

```

## Explanation

### Main Workflow


The ML_Wrapper uses JSON Schemas. If you are unfamiliar with JSON Schemas this [tutorial](https://www.tutorialspoint.com/json/json_schema) can help.


The MLWrapper class handles all administrative overhead regarding
incoming and outgoing MQTT messages.

An instance of this class needs to be provided with information
    about incoming and outgoing topics through a config.ini file.
    Besides, the type of the analysis result
    (either of `"text"`, `"time_series"`, or `"multiple_time_series"`)
    should be given upon instantiation (defaults to `"time_series"`).

As an ML Engineer, a child class of MLWrapper needs to be implemented
    and the run() method needs to be overwritten.
    Here, the main workload of your ML analysis module should be implemented.

The arguments of the run() method need to conform
    to the outputs of retreive_payload_data() and to the inputs
    of the resolve_payload_data() method.
    The latter two can also be customized as needed.
    (The current implementation takes the sensor or analysis data from an
    incoming message, converts them to a pandas dataframe and passes is to
    the run() method.)

In simplified terms, the main analysis workflow looks like the following:

```python
retrieved_data = self.retrieve_payload_data()
result = self.run(*retrieved_data)
message_payload = self.resolve_payload_data(result).
```


In the main program, self.start() shall be used to start an
infinite loop and react to incoming MQTT messages.

### Arguments

Every AnalysisTool inherits from MLWrapper. You can specify The following arguments can be passed for this purpose. 

Argument | Description | Default Value
-------- | -------- | --------
result_type   | Result of analysis tool. Can be ResultType.TIME_SERIES,ResultType.TEXT or ResultType.MULTIPLE_TIME_SERIES   | ResultType.TIME_SERIES,
log_level   | optional from logging enum (e.g. logging.INFO)   | LOG_LEVEL
logger_name | Optional Name for Logger | None
only_react_to_message_type | Only React to SENSOR_UPDATE or ANALYSES_RESULT | None
only_react_to_previous_result_types | optional to set previous result_type required | None
outgoing_message_is_temporary |Required to define whether your result should be stored (False) or just used for following steps (True) | None


### Getting retreived information

The standard information retrieved from the message (a DataFrame, a list
of DataFrames or a dictionary) will be available by the field
`out_message.in_message.retrieved_data` . More fields available are

```
out_message.in_message.columns
out_message.in_message.data
out_message.in_message.metadata
out_message.in_message.timestamp
```

### Returning information 

The return value of the `run` method will be passed to the `resolve_result_data` method of the ML_Wrapper.  This method automatically resolves the data results into a valid payload. 

In general, the `resolve_result_data` method does not need to be overridden. 
 If you want to overwrite this method we encourage you to use the following procedure as
        example for the text result case:
```python
   out_message = await super().resolve_result_data(result, out_message)
   body_dict = out_message.body_as_json_dict
   body_dict["results"]["total"] = "tempered result"
   out_message.body = body_dict
   return out_message
```
This way you will only change the dictionary where required and make sure you have a
        valid json.