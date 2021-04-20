# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.entry import Entry
from openapi_server import util

from openapi_server.models.entry import Entry  # noqa: E501

class ApiResponse(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, code=None, type=None, message=None, result=None, link=None):  # noqa: E501
        """ApiResponse - a model defined in OpenAPI

        :param code: The code of this ApiResponse.  # noqa: E501
        :type code: int
        :param type: The type of this ApiResponse.  # noqa: E501
        :type type: str
        :param message: The message of this ApiResponse.  # noqa: E501
        :type message: str
        :param result: The result of this ApiResponse.  # noqa: E501
        :type result: List[Entry]
        :param link: The link of this ApiResponse.  # noqa: E501
        :type link: str
        """
        self.openapi_types = {
            'code': int,
            'type': str,
            'message': str,
            'result': List[Entry],
            'link': str
        }

        self.attribute_map = {
            'code': 'code',
            'type': 'type',
            'message': 'message',
            'result': 'result',
            'link': 'link'
        }

        self._code = code
        self._type = type
        self._message = message
        self._result = result
        self._link = link

    @classmethod
    def from_dict(cls, dikt) -> 'ApiResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiResponse of this ApiResponse.  # noqa: E501
        :rtype: ApiResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code(self):
        """Gets the code of this ApiResponse.


        :return: The code of this ApiResponse.
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this ApiResponse.


        :param code: The code of this ApiResponse.
        :type code: int
        """

        self._code = code

    @property
    def type(self):
        """Gets the type of this ApiResponse.


        :return: The type of this ApiResponse.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ApiResponse.


        :param type: The type of this ApiResponse.
        :type type: str
        """

        self._type = type

    @property
    def message(self):
        """Gets the message of this ApiResponse.


        :return: The message of this ApiResponse.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this ApiResponse.


        :param message: The message of this ApiResponse.
        :type message: str
        """

        self._message = message

    @property
    def result(self):
        """Gets the result of this ApiResponse.


        :return: The result of this ApiResponse.
        :rtype: List[Entry]
        """
        return self._result

    @result.setter
    def result(self, result):
        """Sets the result of this ApiResponse.


        :param result: The result of this ApiResponse.
        :type result: List[Entry]
        """

        self._result = result

    @property
    def link(self):
        """Gets the link of this ApiResponse.


        :return: The link of this ApiResponse.
        :rtype: str
        """
        return self._link

    @link.setter
    def link(self, link):
        """Sets the link of this ApiResponse.


        :param link: The link of this ApiResponse.
        :type link: str
        """

        self._link = link