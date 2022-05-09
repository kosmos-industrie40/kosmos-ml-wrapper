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

Then you subscribe to the broker with: 

```
mosquitto_sub -t '#' -h 0.0.0.0
```

You will receive every MQTT Message from every Topic. To subscribe to a specific topic, replace `'#'` with the specific topic.


## Simple Usecase

We will use an [Example Analysis Tool](https://gitlab.inovex.de/proj-kosmos/libraries/python/ml_wrapper/-/blob/master/src/examples/usage_example.py). It listens to Messages to the topic `kosmos/analytics/model-test/tag-test`. When it gets a message on this topic it will return  an dict with the key `ind` containing the list [0,1,2,3,4,5,6,7,8,9] on the topic `kosmos/analyses/abc`

After inspecting [example.py](https://gitlab.inovex.de/proj-kosmos/libraries/python/ml_wrapper/-/blob/master/src/examples/usage_example.py) you can then start the Analysis Tool with: 

```python
python example.py
```
To send a MQTT Message to the topic `kosmos/analytics/model-test/tag-test` you can used following command:

You can inspect the [Example Json Files](https://gitlab.inovex.de/proj-kosmos/libraries/python/ml_wrapper/-/tree/master/src/ml_wrapper/messaging/json_handling/kosmos_json_specifications/mqtt_payloads/ml-trigger) - if needed. 

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
