from config import config
import urllib
import urllib.request
import json

def search_knowledge_graph(**params):
    api_key = config["API"]["knowledge_graph_key"]
    service_url = "https://kgsearch.googleapis.com/v1/entities:search"
    default_params = {
        "limit": 20,
        "languages": "en",
        "key": api_key,
        "prefix": False
    }
    params = default_params | params

    url = service_url + "?" + urllib.parse.urlencode(params)
    response_data = urllib.request.urlopen(url).read()
    return json.loads(response_data)

def search_custom_search(**params):
    api_key = config["API"]["custom_search_key"]