# coding: utf-8

from __future__ import absolute_import
import unittest
from unittest.mock import patch
from unittest.mock import Mock

from flask import json
from six import BytesIO

from openapi_server.models.api_response import ApiResponse  # noqa: E501
from openapi_server.models.entry import Entry  # noqa: E501
from openapi_server.models.query import Query  # noqa: E501
from openapi_server.test import BaseTestCase
from openapi_server.controllers import text_controller

from veriservice import veriservice_pb2 as pb
from openapi_server.logic.text_data import embed, SearchAPI


def mocked_search_api():
    veri_client_mock = Mock()
    expected_result = [
        pb.ScoredDatum(
            score=0.9,
            datum=pb.Datum(
                key=pb.DatumKey(
                    feature=embed("text1").tolist(),
                    groupLabel="{\"title\":\"title1\"}".encode(),
                    size1=1,
                    size2=0,
                    dim1=512,
                    dim2=0,
                ),
                value=pb.DatumValue(
                    version=None,
                    label="{\"text\":\"text1\"}".encode(),
                ),
            )
        )

    ]
    veri_client_mock.search.return_value = expected_result
    return SearchAPI("test", client=veri_client_mock)


@patch('openapi_server.controllers.text_controller.search_api', mocked_search_api())
class TestTextController(BaseTestCase):
    """TextController integration test stubs"""

    def test_autocomplete(self):
        """Test case for autocomplete

        Autocomplete entries with text
        """
        body = {
          "texts" : [ "texts", "texts" ],
          "context" : [ "context", "context" ],
          "options" : {
            "key" : "{}"
          }
        }
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/v0/autocomplete',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_insert(self):
        """Test case for insert

        Inserts a list of entries with given input array
        """
        body = [{
          "label" : "label",
          "title" : "title"
        }]
        headers = { 
            'Content-Type': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/v0/insert',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search(self):
        """Test case for search

        Search entries with text
        """
        body = {
          "texts" : [ "texts", "texts" ],
          "context" : [ "context", "context" ],
          "options" : {
            "key" : "{}"
          }
        }
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/v0/search',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
