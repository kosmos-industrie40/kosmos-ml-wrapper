"""
Utility Module to convert data to and from json-usable format.
"""
import datetime
import json
import re
from datetime import timezone
from typing import Union, List
import pandas as pd

JSON_TYPES = {"number": "float64", "string": "str", "rfctime": "datetime64"}


def retrieve_dataframe(results: dict) -> (pd.DataFrame, List[dict], List[dict]):
    """
    Convert the data contained in the results section of
    an MQTT message payload to a Pandas DataFrame.

    :param results: Message payload containing the results and column specification
    :returns dataframe: Payload results converted to Dataframe
    :returns columns: Specification about column types and names
    :returns data: Data from payload in list-representation
    """
    data = results.get("data")
    data = list(map(list, zip(*data)))  # transpose data

    columns = results.get("columns")
    column_names = [col.get("name") for col in columns]
    column_types = {col.get("name"): JSON_TYPES.get(col.get("type")) for col in columns}

    dataframe = pd.DataFrame(data=data, columns=column_names)
    dataframe = dataframe.astype(dtype=column_types)
    return dataframe, columns, data


def retrieve_data(
    payload: str,
) -> (Union[pd.DataFrame, None], List[dict], List[dict], Union[List[dict], None], str):
    """
    Convert the data contained in an MQTT message payload
    to a usable format for ML applications.

    FIXME: 'text' and 'multiple_time_series' datatypes not supported.
    https://gitlab.inovex.de/proj-kosmos/kosmos-mqtt-reaction/-/issues/5

    :param payload: MQTT message payload as a string
    :returns dataframe: Payload results converted to Dataframe
    :return columns: Specification about column types and names
    :return data: Data from payload in list-representation
    :return metadata: List of dictionaried containing metadata about the data and data acquisition
    :return timestamp: Timestamp of the incoming message
    """
    try:
        payload_dict = json.loads(payload)
    except ValueError as error:
        raise ValueError("No valid json was provided: {}".format(error)) from error
    payload_type = payload_dict.get("type")
    metadata = None
    timestamp = payload_dict.get("timestamp")
    if payload_type == "time_series":
        results = payload_dict.get("results")
        if results is not None:
            dataframe, columns, data = retrieve_dataframe(results)
            # NB: timestamp should never be None

        else:
            raise Exception("Error! No Results obtained.")
    elif payload_type == "text":
        results = payload_dict.get("results")
        if results is not None:
            results_string = [json.dumps(results)]
            column_name = ["text_result"]
            columns = [{"name": column_name, "type": "string"}]
            dataframe = pd.DataFrame(data=results_string, columns=column_name)
            data = results

    elif payload_type == "multiple_time_series":
        results = payload_dict.get("results")
        if results is not None:
            pass

    # assume new sensor data in this case instead of analyses results
    elif payload_type is None:
        return retrieve_sensor_update_data(payload_dict), timestamp
    else:
        raise Exception(f"Error while reading payload type {payload_type}")

    return dataframe, columns, data, metadata, timestamp


def retrieve_sensor_update_data(payload: dict):
    """
    This method retrieves the data of a data-formal.json payload
    :param payload: dict
    :return dataframe: Payload results converted to Dataframe
    :return columns: Specification about column types and names
    :return data: Data from payload in list-representation
    :return metadata: List of dictionary containing metadata about the data and data acquisition
    :return timestamp: Timestamp of the incoming message
    """
    data = payload.get("data")
    data = list(map(list, zip(*data)))  # transpose data

    columns = payload.get("columns")
    column_names = [col.get("name") for col in columns]
    column_types = {col.get("name"): JSON_TYPES.get(col.get("type")) for col in columns}

    dataframe = pd.DataFrame(data=data, columns=column_names)
    dataframe = dataframe.astype(dtype=column_types)

    metadata = payload.get("meta")
    return dataframe, columns, data, metadata


def resolve_data_frame(dataframe: pd.DataFrame) -> (list, list):
    """
    Turns a data_frame into two list usable as a json payload.
    First list is the columns, second list is the data.
    """
    assert isinstance(
        dataframe, pd.DataFrame
    ), "Only dataframes are allowed in function resolve_data_frame"
    column = [
        {"name": name, "type": type_}
        for name, type_ in list(
            zip(dataframe.dtypes.keys(), [str(a) for a in dataframe.dtypes.values])
        )
    ]
    data = dataframe.astype(str).values.tolist()
    for col_dict_i, col_dict in enumerate(column):
        type_ = col_dict["type"]
        if re.findall("(int.*)|(float.*)", type_):
            type_ = "number"
        elif re.findall("(datetime.*)", type_):
            type_ = "rfctime"
        else:
            type_ = "string"
        column[col_dict_i]["type"] = type_

    return column, data


def resolve_data(
    data: Union[List[pd.DataFrame], pd.DataFrame, dict], resulttype: str
) -> dict:
    """
    Formats the result from the analysis workflow so that it is
    usable as json payload.

    FIXME: Analysis output for 'text' resulttype still not entirely clear.
    Need to discuss the data structure of such a function's returned data structure.
    https://gitlab.inovex.de/proj-kosmos/kosmos-mqtt-reaction/-/issues/5

    :param resulttype: The type of the return value of the analysis function.
        Can either be "text", "time_series", or "multiple_time_series".
    :return schema: Dictionary containing the analysis result in a structure
        that conforms to the defined json schema.
    """
    if resulttype == "time_series":
        schema = {}
        schema["type"] = resulttype
        columns, data_ = resolve_data_frame(data)

        schema["results"] = {}
        schema["results"]["data"] = data_
        schema["results"]["columns"] = columns

    elif resulttype == "text":
        total = data.get("total")
        predict = data.get("predict")

        assert total is not None, "Field 'total' in text result is required."
        assert predict is not None, "Field 'predict' in text result is required."
        schema = {}
        schema["type"] = resulttype
        schema["results"] = data

    elif resulttype == "multiple_time_series":
        schema = {}
        schema["type"] = resulttype
        schema["results"] = []

        assert isinstance(data, list)
        for i, dataframe in enumerate(data):
            columns, data_ = resolve_data_frame(dataframe)

            schema["results"].append({})
            schema["results"][i]["data"] = data_
            schema["results"][i]["columns"] = columns

    else:
        raise Exception(f"Error! Resulttype {resulttype} is not supported.")

    schema["timestamp"] = (
        datetime.datetime.utcnow().astimezone(timezone.utc).isoformat(sep="T")
    )
    return schema
