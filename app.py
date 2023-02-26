"""
Spotify api
"""
import doctest
import json
import os
import base64
from dotenv import load_dotenv
import requests
import pycountry

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_auth_header(token):
    """
    Returns auth header with provided token
    >>> get_auth_header("token")
    {'Authorization': 'Bearer token'}
    """
    return {'Authorization': 'Bearer ' + token}


def get_token():
    """
    Returns access token
    """
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("UTF-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "UTF-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    results  = requests.post(url, headers = headers, data = data)
    json_result = json.loads(results.content)
    token = json_result["access_token"]

    return token
