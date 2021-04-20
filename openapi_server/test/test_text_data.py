# coding: utf-8

from __future__ import absolute_import
import unittest
from openapi_server.test import BaseTestCase

from openapi_server.logic.text_data import TextItem, TextData, embed
from unittest.mock import Mock

from veriservice import veriservice_pb2 as pb

class TestEmbed(BaseTestCase):

    def test_embed(self):
        vector = embed("Apple.")
        self.assertEqual(len(vector), 512)

class TestTextItem(BaseTestCase):

    def test_text_item(self):
        info = "{id:'id0'}"
        text = "Who let the Dogs out? Who? Who?"
        item= TextItem(info=info, text=text)
        item.calculate_texts()
        texts = item.get_texts()
        texts.sort()
        self.assertEqual(2, len(texts))
        self.assertEqual("Who let the Dogs out?", texts[0])
        self.assertEqual("Who?", texts[1])

        item.add_text("Minor Addition.")
        item.calculate_texts()
        texts = item.get_texts()
        texts.sort()
        self.assertEqual(3, len(texts))
        self.assertEqual("Minor Addition.", texts[0])
        self.assertEqual("Who let the Dogs out?", texts[1])
        self.assertEqual("Who?", texts[2])

        count = 0
        for entry in item.get_entries():
            self.assertEqual(entry["group_label"], info)
            self.assertEqual(len(entry["feature"]), 512)
            count = count + 1

        self.assertEqual(3, count)

    def test_text_item_increase_split_threshold_min(self):
        info = "{id:'id1'}"
        text = "Who let the Dogs out? Who? Who?"
        item = TextItem(info=info, text=text, split_threshold_min=100)
        item.calculate_texts()
        texts = item.get_texts()
        texts.sort()
        self.assertEqual(1, len(texts))
        self.assertEqual(text, texts[0])


class TestTextData(BaseTestCase):

    def test_text_data_insert(self):
        veri_client_mock = Mock()
        veri_client_mock.insert.return_value = None
        text_data = TextData(veri_client_mock)
        info = "{id:'id0'}"
        text = "Who let the Dogs out? Who? Who?"
        item = TextItem(info=info, text=text)
        text_data.insert(item)
        veri_client_mock.insert.assert_called()
        self.assertEqual(True, True)

    def test_text_data_item_search(self):
        veri_client_mock = Mock()
        expected_result = [
            pb.ScoredDatum(
                score=0.9,
                datum=pb.Datum(
                    key=pb.DatumKey(
                        feature=embed("text1").tolist(),
                        groupLabel="{\"id\":\"id1\"}".encode(),
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
        text_data = TextData(veri_client_mock)
        text = "Who let the Dogs out? Who? Who?"
        result = text_data.search(text)
        veri_client_mock.search.assert_called()
        self.assertEqual(len(result), 1)