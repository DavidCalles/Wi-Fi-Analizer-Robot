from urllib import request
import requests as rq
from requests.exceptions import HTTPError
import json
from datetime import datetime


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
        return json_response
    

def postRequestJSON(url, dict):
    try:
        dict['DateTime'] = str(datetime.now())
        response = rq.post(url, json=dict)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        return json_response
    
    
def putRequestJSON(url, dict):
    try:
        dict['DateTime'] = str(datetime.now())
        response = rq.put(url, json=dict)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        return json_response
    
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
        return json_response
    

topic = "/Cats"
cat1 = {'name':'Garfield', 'color':'orange', 'mood':'hungry'}
response = postRequestJSON(url=url+topic, dict=cat1)
print(json.dumps(response, indent=4, sort_keys=True))

cat2 = {'name':'Unlucky', 'color':'black', 'mood':'lazy'}
response = postRequestJSON(url=url+topic, dict=cat2)
print(json.dumps(response, indent=4, sort_keys=True))

response = getRequestJSON(url+topic)
print(json.dumps(response, indent=4, sort_keys=True))