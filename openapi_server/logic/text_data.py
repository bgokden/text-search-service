import os
import json
from typing import List, Generator, Dict

import spacy
from veriservice import VeriClient
import numpy as np
import pandas as pd
import spacy_universal_sentence_encoder
# load one of the models: ['en_use_md', 'en_use_lg', 'xx_use_md', 'xx_use_lg']
nlp = spacy_universal_sentence_encoder.load_model('xx_use_lg')
import tensorflow_text

def embed(text: str) -> np.ndarray:
    """
    Return vector representation of given text
    :param text:
    :return: 512 float ndarray
    """
    n = nlp(text)
    return n.vector


class TextItem:
    """
    Text item is a representation of text that can be converted into veri entries
    Text can be added as multiple parts or as one part that can be split into sentences.
    """
    def __init__(self, info: str = None, text=None, split_threshold_min=20):
        """
        Initize a text item
        :param info: recommended to be a json metedata information.
        :param text: string or list of string that is included in the text item.
        :param split_threshold_min: minimum threshold to be split into sentences
        """
        self.info = info
        self.texts = []
        if text is not None:
            if isinstance(text, str):
                self.texts = [text]
            elif isinstance(text, list):
                self.texts = text
            else:
                self.texts = str(text)
        self.split_threshold_min = split_threshold_min

    def add_text(self, text: str) -> None:
        """
        Add a text to text_item
        :param text:
        :return: None
        """
        if isinstance(text, str):
            self.texts.append(text.strip().rstrip("\n"))

    def calculate_texts(self) -> None:
        """
        Split texts into sentences and deduplicate text entries
        :return: None
        """
        texts = []
        for text in self.texts:
            paragraphs = list(filter(lambda x: x != '', text.split('\n\n')))
            for paragraph in paragraphs:
                text = paragraph.replace("\n", " ").strip()
                if len(text) > self.split_threshold_min:
                    text_sentences = nlp(text)
                    sentences = []
                    for sentence in text_sentences.sents:
                        current = sentence.text
                        sentences.append(current.strip())
                    texts.extend(sentences)
                else:
                    texts.append(text)
        self.texts = list(set(texts))

    def get_texts(self) -> List[str]:
        """
        Returns list of current texts
        :return: List of string
        """
        return self.texts

    def get_info(self) -> str:
        """
        Return current info as tring
        :return: string
        """
        return self.info

    def get_entries(self) -> Generator[Dict, None, None]:
        """
        Generate entries for Veri
        :return: Generator to Json Entries that can be inserted to Veri
        """
        self.calculate_texts()
        for text in self.texts:
            feature = embed(text)
            yield {'label': json.dumps({"text": text}), 'group_label': self.info, 'feature': feature.tolist()}

    def get_features(self) -> Generator[np.ndarray, None, None]:
        """
        This is an utility method to just generate embedding vectors.
        :return: Generator to Feature Vector to text
        """
        for text in self.texts:
            yield embed(text)


class TextData:
    """
    Data Wrapper to query text or insert items to Veri
    """
    def __init__(self,
                 client: VeriClient,
                 limit=200,
                 group_limit=5,
                 timeout=100000,
                 result_limit=10,
                 score_func_name="AnnoyCosineSimilarity",
                 higher_is_better=True,
                 cache_duration=60,
                 prioritize_context=False):
        """
        Initlize a TextData to use search/insert functions of Veri

        :param client: Veri Client to use as backend to Data
        :param limit: Limit of top entries used in query
        :param group_limit: Limit of top entries used in query after grouping by group label
        :param timeout: Query timeout in milliseconds
        :param result_limit: Limit of the number results to return
        :param score_func_name: Similarity Algorithm to use when querying eg:.AnnoyCosineSimilarity, CosineSimilarity
        :param higher_is_better: Boolean value that defines the score order based on score function
        :param cache_duration: The duration in seconds to store in the Veri instance internal cache
        :param prioritize_context: Boolean value that defines if the context is more important than query
        """
        self.client = client
        self.limit = limit
        self.group_limit = group_limit
        self.timeout = timeout
        self.result_limit = result_limit
        self.score_func_name = score_func_name
        self.higher_is_better = higher_is_better
        self.prioritize_context = prioritize_context
        self.cache_duration = cache_duration

    def insert(self, item) -> None:
        """
        Inserts a text item to veri
        :param item: a text item that represents one or multiple texts
        :return: None
        """
        for entry in item.get_entries():
            self.client.insert(entry['feature'], entry['label'].encode(), group_label=entry['group_label'].encode())

    def search(self, text, context=[], **kwargs) -> pd.DataFrame:
        """
        Utility method to query veri for a single text
        :param text: string text to query
        :param context: list of string as context
        :param kwargs: Optional parameters check item_search
        :return: The Query Result as Pandas Dataframe
        """
        item_to_search = TextItem(text=text)
        item_to_search.calculate_texts()
        item_context = TextItem(text=context)
        item_context.calculate_texts()
        return self.item_search(item_to_search, item_context, **kwargs)

    def item_search(self, item, context, **kwargs) -> pd.DataFrame:
        """
        Search a text item in Veri
        :param item: text item to search
        :param context: text item as context
        :param kwargs: Optional parameters
        :return: The Query Result as Pandas Dataframe
        """
        vectors = item.get_features()
        context_vectors = context.get_features()
        positive = kwargs.get('positive', [])
        negative = kwargs.get('negative', [])
        filters = []
        for text in positive:
            filters.append("..#(text%\"{}\")".format(text))
        for text in negative:
            filters.append("..#(text!%\"{}\")".format(text))
        result = self.client.search(vectors,
                                    limit=kwargs.get('limit', self.limit),
                                    group_limit=kwargs.get('group_limit', self.group_limit),
                                    timeout=kwargs.get('timeout', self.timeout),
                                    score_func_name=kwargs.get('score_func_name', self.score_func_name),
                                    higher_is_better=kwargs.get('higher_is_better', self.higher_is_better),
                                    context_vectors=context_vectors,
                                    prioritize_context=kwargs.get('prioritize_context', self.prioritize_context),
                                    cache_duration=kwargs.get("cache_duration", self.cache_duration),
                                    filters=filters,
                                    group_filters=kwargs.get("group_filters", []),
                                    result_limit=kwargs.get('result_limit', self.result_limit))
        results = []
        for r in result:
            group_label_data = json.loads(r.datum.key.groupLabel)
            label_data = json.loads(r.datum.value.label)
            results.append({
                'score': r.score,
                'label': label_data['text'],
                'group_label': group_label_data,
                'feature': r.datum.key.feature,
            })
        rs = pd.DataFrame(results)
        if 'group_label' in rs.columns:
            return pd.concat([rs.drop(['group_label'], axis=1), rs['group_label'].apply(pd.Series)], axis=1)
        return rs



def get_hosts():
    """
    Utility Method to Get Environment Variable
    :return: HOSTS environment variable or default Value.
    """
    return os.getenv('HOSTS', 'localhost:5678')

class SearchAPI:
    """
    Search API to be used in the controller
    """
    def __init__(self, name, client=None, hosts=get_hosts()):
        """
        Initilaize API Wrapper to Veri Text Data
        :param name: name of the dataset
        :param hosts: Comma separated list of network addresses
        """
        self.name = name
        self.client = client
        if self.client is None:
            self.client = VeriClient(hosts, name)
        self.data = TextData(self.client)

    def ready(self):
        """
        This can be used to check if liblaries are loaded.
        :return:
        """
        return True

    def search(self, texts: List[str], context: List[str], options: Dict={}) -> pd.DataFrame:
        """
        Wrapper for text data search
        :param texts: List of string to search
        :param context: List of string as context
        :param options: Optional parameters
        :return: The Query Result as Pandas Dataframe
        """
        item_to_search = TextItem(text=texts)
        item_to_search.calculate_texts()
        item_context = TextItem(text=context)
        item_context.calculate_texts()
        return self.data.item_search(item_to_search, item_context)

    def autocomlete(self, text: str, context: List[str], options: Dict={}):
        """
        Autocmplete is a limited search in dataset.
        :param text: text to complete
        :param context: List of string as context
        :param options: Optional parameters
        :return: The Query Result as Pandas Dataframe
        """
        return self.data.search(text, context=context, group_limit=1, result_limit=5)

    def insert(self, title: str, text: str, options: Dict={}):
        """
        Inserts a data to Veri by conterting it to text item
        :param title:
        :param text:
        :param options:
        :return:
        """
        item = TextItem(info=json.dumps({"title": title}), text=text)
        return self.data.insert(item)