import json
import requests


class HeadersBuilder:
    """
    Class to build headers to external API call

    Author: Matheus Henrique (m.araujo)
    """

    def build_headers(self, header):
        pass


class AuthorizationHeadersBuilder(HeadersBuilder):
    """
    Class to build authentication headers to external API call

    Author: Matheus Henrique (m.araujo)
    """

    def __init__(self, authorization) -> None:
        self.authorization = authorization

    def build_headers(self, header):
        header['Authorization'] = self.authorization
        return header


class ContentTypeHeadersBuilder(HeadersBuilder):
    """
    Class to build contentType headers to external API call

    Author: Matheus Henrique (m.araujo)
    """

    def __init__(self, content_type) -> None:
        self.content_type = content_type

    def build_headers(self, header):
        header['Content-Type'] = self.content_type
        return header


def call_api(endpoint, method, data=None, headers=None, no_headers=False, is_json_response=True):
    """
    Call external API's

    Author: Matheus Henrique (m.araujo)

    Params:
        endpoint: str
        method: str (coices: GET, POST,PUT)
        data: any
        headers: List<AuthorizationHeadersBuilder>
        is_json_response: Bool

    """
    if no_headers:
        default_headers = {}
    else:
        default_headers = {"Content-Type": "application/json; charset=utf-8"}

        if headers:
            for header_builder in headers:
                default_headers = header_builder.build_headers(default_headers)

    try:
        if method == 'GET':
            response = requests.get(url=endpoint, headers=default_headers)
        elif method == 'POST':
            response = requests.post(
                url=endpoint, data=data, headers=default_headers)
        elif method == 'PUT':
            response = requests.put(
                url=endpoint, data=data, headers=default_headers)
        else:
            raise Exception("Method not supported")

        if is_json_response:
            if response.status_code not in [200, 201, 204]:
                raise Exception(json.loads(response.text))

            response = response.json()

        return response
    except Exception as e:
        raise Exception(e)
