# -*- coding: utf-8 -*-

from requests.exceptions import *


class CloudError(HTTPError):
    def __init__(self, description, code, response):
        super(CloudError, self).__init__(description)
        self.code = code
        self.response = response


def cloud_error(response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        data = e.response.json
        if not data:
            raise e
        code = data['code']
        description = data['description']
        raise CloudError(description, code, response)
