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

    TODO: 'text' and 'multiple_time_series' datatypes not supported.

    :param payload: MQTT message payload as a string
    :returns dataframe: Payload results converted to Dataframe
    :return columns: Specification about column types and names
    :return data: Data from payload in list-representation
    :return metadata: List of dictionaried containing metadata about the data and data acquisition
    :return timestamp: Timestamp of the incoming message
    """
    try:
        payload_dict = json.loads(payload)
    except ValueError as e:
        raise ValueError("No valid json was provided: %s".format(e))
    payload_type = payload_dict.get("type")
    metadata = None
    if payload_type == "time_series":
        results = payload_dict.get("results")
        if results is not None:
            dataframe, columns, data = retrieve_dataframe(results)
            timestamp = payload_dict.get("timestamp")
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

            timestamp = payload_dict.get("timestamp")

    elif payload_type == "multiple_time_series":
        results = payload_dict.get("results")
        if results is not None:
            pass

    # assume new sensor data in this case instead of analyses results
    elif payload_type is None:
        data = payload_dict.get("data")
        data = list(map(list, zip(*data)))  # transpose data

        columns = payload_dict.get("columns")
        column_names = [col.get("name") for col in columns]
        column_types = {
            col.get("name"): JSON_TYPES.get(col.get("type")) for col in columns
        }

        dataframe = pd.DataFrame(data=data, columns=column_names)
        dataframe = dataframe.astype(dtype=column_types)

        metadata = payload_dict.get("meta")

        timestamp = payload_dict.get("timestamp")
    else:
        raise Exception(f"Error while reading payload type {payload_type}")

    return dataframe, columns, data, metadata, timestamp


def resolve_data_frame(dataframe: pd.DataFrame) -> (list, list):
    """
    Turns a data_frame into two list usable as a json payload.
    First list is the columns, second list is the data.
    """
    # pylint: disable=fixme
    # TODO: Take the mapping information out of the docs git module
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

    TODO: Analysis output for 'text' resulttype still not entirely clear. Need
    to discuss the data structure of such a function's returned data structure.

    :param resulttype: The type of the return value of the analysis function.
        Can either be "text", "time_series", or "multiple_time_series".
        (TODO: Need to define correct structure of "text" type.)
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
