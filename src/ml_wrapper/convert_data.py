"""
Utility Module to convert data to and from json-usable format.
"""
import re
from typing import List
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
