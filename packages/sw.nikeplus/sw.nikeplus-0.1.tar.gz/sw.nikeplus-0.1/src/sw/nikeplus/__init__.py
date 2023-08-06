from sw.nikeplus.fetcher import NikePlusFetcher
from sw.nikeplus.utils import xml2json


def get_xml(user_id, force=False):
    fetcher = NikePlusFetcher(user_id)
    status, response = fetcher.fetch(force)
    return response


def get_json(user_id, force=False):
    xml_string = get_xml(user_id, force)
    return xml2json(xml_string)
