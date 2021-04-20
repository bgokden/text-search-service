import connexion
import six

from openapi_server.models.api_response import ApiResponse  # noqa: E501
from openapi_server.models.entry import Entry  # noqa: E501
from openapi_server.models.query import Query  # noqa: E501
from openapi_server import util
from openapi_server.logic.text_data import SearchAPI

search_api = SearchAPI("news")

def autocomplete(body, user, token_info):  # noqa: E501
    """Autocomplete entries with text

    Autocomplete entries with text and additional parameters # noqa: E501

    :param body: Query text with context
    :type body: dict | bytes

    :rtype: ApiResponse
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501
        df_result = search_api.autocomlete(body.texts.pop(), body.context, body.options)
        entry_list = []
        for index, row in df_result.iterrows():
            entry_list.append(Entry(row['title'], row['label']))
        return ApiResponse(code=0, type="Success", message="", result=entry_list, link="")
    return ApiResponse(code=1, type="Failure", message="Failure", result=[], link="")


def insert(body, user, token_info):  # noqa: E501
    """Inserts a list of entries with given input array

     # noqa: E501

    :param body: Insert a new entry
    :type body: list | bytes

    :rtype: Empty Dict
    """
    if connexion.request.is_json:
        body = [Entry.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
        for entry in body:
            search_api.insert(entry.title, entry.label)
    return {}


def search(body, user, token_info):  # noqa: E501
    """Search entries with text

    Search entries with text and additional parameters # noqa: E501

    :param body: Query text with context
    :type body: dict | bytes

    :rtype: ApiResponse
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501
        df_result = search_api.search(body.texts, body.context, body.options)
        entry_list = []
        for index, row in df_result.iterrows():
            entry_list.append(Entry(row['title'], row['label']))
        return ApiResponse(code=0, type="Success", message="", result=entry_list, link="")
    return ApiResponse(code=1, type="Failure", message="Failure", result=[], link="")
