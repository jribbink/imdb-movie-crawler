from config import config
import json
import requests

def search_knowledge_graph(**params):
    api_key = config["API"]["knowledge_graph_key"]
    service_url = "https://kgsearch.googleapis.com/v1/entities:search"
    default_params = {
        "limit": 20,
        "languages": "en",
        "key": api_key,
        "prefix": False,
    }
    params = default_params | params

    response_data = requests.get(service_url, params)
    return response_data.json()

def search_custom_search(**params):
    key = config["API"]["custom_search_key"]
    search_context = config["API"]["custom_search_cx"]
    service_url = "https://www.googleapis.com/customsearch/v1"

    default_params = {
        "key": key,
        "cx": search_context,
    }
    params = default_params | params

    response_data = requests.get(service_url, params)
    return response_data.json()

