from urllib import request
import requests as rq
from requests.exceptions import HTTPError

url = "https://crudcrud.com/api/3b17854564c1460dac2b6318c1f7a29b"

def getRequestJSON(url):
    try:
        response = rq.get(url)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        return json_response, json_response['headers']['Content-Type']
    

def postRequestJSON(url, dict):
    try:
        response = rq.post(url, json=dict)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        return json_response, json_response['headers']['Content-Type']
    
    
def putRequestJSON(url, dict):
    try:
        response = rq.put(url, json=dict)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        return json_response, json_response['headers']['Content-Type']
    
def deleteRequestJSON(url):
    try:
        response = rq.delete(url)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        return json_response, json_response['headers']['Content-Type']