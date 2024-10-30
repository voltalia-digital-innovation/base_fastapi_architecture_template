import json
import re
import time
import base64
import hashlib
import calendar
import numpy as np
from typing import List
from pandas import DataFrame
from functools import reduce
from unidecode import unidecode
from datetime import datetime, timedelta
from modules.core.env import (
    ANALYTICS_APPLICATION_PASSWORD, ANALYTICS_APPLICATION_USER,
    ANALYTICS_LOGIN_ROUTE
)
from modules.core.services.utils.external_apis import call_api


def deep_get(_dict, keys, default=None):
    def _reducer(d, key):
        if isinstance(d, dict):
            return d.get(key, default)
        if isinstance(d, list):
            try:
                return d[key]
            except IndexError:
                return default
        return default
    return reduce(_reducer, keys, _dict)


def pretty_time_delta(seconds):
    seconds = abs(int(seconds))
    if seconds == 0:
        return '0 segundo'
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    params = []
    if days > 0:
        params.append((days, 'dias' if days > 1 else 'dia'))
    if hours > 0:
        params.append((hours, 'horas' if hours > 1 else 'hora'))
    if minutes > 0:
        params.append((minutes, 'minutos' if minutes > 1 else 'minuto'))
    if seconds > 0:
        params.append((seconds, 'segundos' if seconds > 1 else 'segundo'))

    params = ["{} {}".format(*x) for x in params]
    if len(params) == 1:
        return params[0]
    return ", ".join(params[:-1]) + " e " + params[-1]


def format_series_numbers_by_columns(
        dataframe: DataFrame, columns: List[str]
) -> DataFrame:
    """
    Will format all values in selected columns with thousands and decimal separator
    Modifications will be made as "inplace" method. But the dataframe will be returned too.
    """
    for column in columns:
        dataframe[column] = dataframe[column].dropna().astype(float).apply(
            lambda value: "{:,.1f}".format(value).replace(
                '.', '|').replace(',', '.').replace('|', ',')
        )
    return dataframe


def string_to_hash256(string: str, random: bool = False):
    if string:
        if random:
            string = string + str(time.time())
        hash256_string = hashlib.sha256(string.encode('UTF-8'))
        return hash256_string.hexdigest()


def pdf_file_to_base64(pdf: bytes):
    base64_file = base64.b64encode(pdf).decode('utf-8')

    return base64_file


def get_file_from_request(request, mime_type: List[str] = None):
    """
    Will retrieve the first file of request, or raise exception if file does not exist
    """
    file = request.FILES.getlist('file')

    if len(file) < 1:
        if mime_type and file[0].content_type not in mime_type:
            raise Exception(
                f"You must send a file with one this formats: [{str(mime_type)}]")
        raise Exception("You must send a file!")

    return file[0]


def get_files_from_request(request, request_file_name: str, mime_type: List[str] = None):
    """
    Will retrieve all files of request, or raise exception if a file does not exist
    """
    files = request.FILES.getlist(request_file_name)

    for file in files:
        if len(file) < 1:
            if mime_type and file[0].content_type not in mime_type:
                raise Exception(
                    f"You must send a file with one this formats: [{str(mime_type)}]")
            raise Exception("You must send a file!")

    return files


def format_name(full_name: str):
    """
    Will return "full_name" in format: "First S. T. Any. Last"
    """

    # Split full_name
    splitted_name = full_name.split(' ')

    # Remove 2 characters names
    for index, full_name in enumerate(splitted_name):
        if len(full_name) < 3:
            splitted_name.pop(index)

    # Abbreviate middle names
    for index, full_name in enumerate(splitted_name):
        # Abbreviate only middle names
        if index > 0 and index < len(splitted_name) and index != len(splitted_name) - 1:
            splitted_name[index] = f"{str(full_name[0]).upper()}."

    # Concatenate names
    formatted_name = ' '.join(splitted_name)

    return formatted_name.strip()


def extract_domain(email: str) -> str:
    pattern = r"@([A-Za-z0-9.-]+)\."
    match = re.findall(pattern, email)
    return match[0] if match else ''


def excel_columns_to_sql_columns(untreated_columns_names: List[str]):
    columns = []
    for item in untreated_columns_names:
        name_without_accents = unidecode(
            item.replace('(', '').replace(')', '').replace(
                '/', '_').replace('-', '_').strip().lower()
        )

        name_splitted = re.findall(r'\S+', name_without_accents)

        columns.append('_'.join(name_splitted))

    return columns


def has_consecutive_hyphens(input_string: str):
    pattern = r'-{2,}'
    return bool(re.search(pattern, input_string))


def get_analytics_token_from_credentials(username: str = None, password: str = None) -> str:
    auth = None

    if username and password:
        auth = {
            "username": username,
            "password": password,
        }
    else:
        auth = {
            "username": ANALYTICS_APPLICATION_USER,
            "password": ANALYTICS_APPLICATION_PASSWORD
        }

    token_request = call_api(endpoint=ANALYTICS_LOGIN_ROUTE + '/',
                             method='POST', data=auth, no_headers=True)

    return token_request['access']


def time_debugger(start_datetime, end_datetime):
    diff_timedelta = end_datetime - start_datetime
    return str(timedelta(seconds=diff_timedelta.seconds))


def value_or_null(value):
    return value if value is not None else 'NULL'


def value_or_none(value):
    return None if np.isnan(value) else value


def dict_to_list_of_tuples(dic: dict):
    return [(str(key), str(value)) for key, value in dic.items()]


def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def references_are_valid(start_reference, end_reference):
    """Expected format: yyyy-MM-dd"""
    try:
        start_reference = datetime.strptime(start_reference, '%Y-%m-%d')
        end_reference = datetime.strptime(end_reference, '%Y-%m-%d')
        if start_reference > end_reference or end_reference > datetime.now():
            return False
    except:
        return False
    return True


def get_exception_detail_message(error: Exception):
    try:
        # Try to convert the string to JSON
        return json.loads(str(error))
    except json.JSONDecodeError:
        # If it fails, return the original string
        return str(error)


def is_a_valid_month(month: any):
    is_valid_type = isinstance(month, int) or (
        isinstance(month, str) and month.isdigit())
    return is_valid_type and int(month) <= 12 and int(month) >= 1
