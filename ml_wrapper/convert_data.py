"""
Utility Module to convert data to and from json-usable format.
"""
import datetime
import json
from datetime import timezone
from typing import Union, List
import pandas as pd

JSON_TYPES = {"number": "float64", "string": "str"}


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
) -> (Union[pd.DataFrame, None], List[dict], List[dict], Union[List[dict], None], int):
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

    payload_dict = json.loads(payload)
    payload_type = payload_dict.get("type")
    metadata = None
    if payload_type == "time_series":
        results = payload_dict.get("results")
        if results is not None:
            dataframe, columns, data = retrieve_dataframe(results)
            timestamp = int(
                payload_dict.get("date")
            )  # NB: timestamp should never be None

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

            timestamp = int(payload_dict.get("date"))

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

        timestamp = int(payload_dict.get("timestamp"))
    else:
        raise Exception(f"Error while reading payload type {payload_type}")

    return dataframe, columns, data, metadata, timestamp


def convert_datatypes(datatype: str) -> str:
    """
    The defined json schema only accepts datatypes 'number' or 'string'.
    Based on the present python datatype, this function maps that datatype
    to either of 'number' or 'string'.

    :param datatype: The python datatype of any result
    :return analysis_datatype: Json schema-conform datatype.
        Can either be "number" or "string"
    """
    # else-case for better readability
    # pylint: disable=no-else-return
    if "float" in datatype or "int" in datatype or "double" in datatype:
        return "number"
    if "str" in datatype or "string" in datatype or "object" in datatype:
        return "string"
    else:
        raise Exception(f"Error! Datatype {datatype} is not supported.")


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
        values = data.astype(str).values.T.tolist()
        columns = data.columns.to_list()
        dtypes = data.dtypes.values

        schema["results"] = {}
        schema["results"]["data"] = values
        schema["results"]["columns"] = []
        for i, col in enumerate(columns):
            schema["results"]["columns"].append(
                {"name": col, "type": convert_datatypes(dtypes[i].name)}
            )

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
            values = dataframe.astype(str).values.T.tolist()
            columns = dataframe.columns.to_list()
            dtypes = dataframe.dtypes.values

            schema["results"].append({})
            schema["results"][i]["data"] = values
            schema["results"][i]["columns"] = []
            for j, col in enumerate(columns):
                schema["results"][i]["columns"].append(
                    {"name": col, "type": convert_datatypes(dtypes[j].name)}
                )

    else:
        raise Exception(f"Error! Resulttype {resulttype} is not supported.")

    schema["date"] = (
        datetime.datetime.utcnow().astimezone(timezone.utc).isoformat(sep="T")
    )
    return schema
