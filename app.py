"""
Spotify api
"""
# import doctest
import json
import os
import base64
import pandas as pd
from dotenv import load_dotenv
import requests
from flask import Flask, render_template, request
import folium

saved_data = {}

app = Flask(__name__)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
countries = pd.read_csv('countries.csv')


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
    results  = requests.post(url, headers = headers, data = data, timeout=10)
    json_result = json.loads(results.content)
    token = json_result["access_token"]

    return token


def search_artist(token, artist_name):
    """
    Finds artist from given artist_name and valid access token.
    Returns in json format.
    >>> token = get_token()
    >>> search_artist(token, "kalush")["artists"]["items"][0]["name"]
    'KALUSH'
    >>> search_artist(token, "RHCP")["artists"]["items"][0]["name"]
    'Red Hot Chili Peppers'
    >>> search_artist(token, "Антитіла")["artists"]["items"][0]["name"]
    'Antytila'
    """
    url = 	f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    results = requests.get(url, headers=get_auth_header(token), timeout=10)
    json_result = json.loads(results.content)
    return json_result

def get_markets(song_id, token):
    """
    Finds available markets for given song_id and valid access token.
    Returns in json format.
    >>> token = get_token()
    >>> 'ET' in get_markets("2vHzOWRKYPLu8umRPIFuOq",token)
    True
    >>> "PL" in get_markets("44FopWyaddRoiuNrD8hlUw", token)
    True
    >>> "AO" in get_markets("7exHT4swWOKL5addPeqkLP", token)
    True
    """
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    results = requests.get(url, headers=get_auth_header(token), params={"country":"US"}, timeout=10)
    available_markets = json.loads(results.content)["available_markets"]
    return available_markets

def top_track(artist_id, token):
    """
    Finds top tracks for artist with artist_id using valid access token.
    Returns in json format.
    >>> token = get_token()
    >>> top_track("46rVVJwHWNS7C7MaWXd842", token)[0]["name"]
    'Stefania (Kalush Orchestra)'
    >>> top_track("5sc9td6C7xxPa3mOmmvXPu", token)[0]["name"]
    'Фортеця Бахмут'
    >>> top_track("5lLVx3mMyUvZ9QKzM09CZa", token)[0]["name"]
    'Тримай'
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    results = requests.get(url, headers=get_auth_header(token), timeout=10)
    json_result = json.loads(results.content)["tracks"]

    return json_result

@app.route("/")
def search_form():
    """Endpoint for search form"""
    return render_template("index.html")

@app.route("/search")
def search_markets():

    """ Endpoint for map """
    # Get token
    token = get_token()

    # Get artist json object and id
    artist_name = request.args.get('artist')
    atrist = None
    try:
        atrist = search_artist(token, artist_name)["artists"]["items"][0]
    except (KeyError, IndexError):
        return render_template("error.html", artist = artist_name)

    # Get top track and available markets
    track = top_track(atrist["id"], token)[0]
    markets = get_markets(track["id"], token)

    # Create map
    map = folium.Map()
    folium_g = folium.FeatureGroup(name=track["name"])

    for _, country_code in enumerate(markets):
        country = countries.loc[countries['ISO 3166 Country Code'] == country_code].to_dict("list")
        if country["Country"]:
            folium_g.add_child(folium.Marker(location=[country["Latitude"][0],
                                                        country["Longitude"][0]],
                                popup=country["Country"][0],
                                icon=folium.Icon()))

    map.add_child(folium_g)
    map.add_child(folium.LayerControl())
    return ("<div>"+"<a target='_blank' style='background-color: #f44336;\
               color: white;padding: 14px 25px;text-align:center;\
               text-decoration:none;display: inline-block;' href='http://127.0.0.1:5000/'>Back</a>"+
               "<h1 style='font-family:verdana; color: #665000; text-align: center; f'>"+
               "Artist - "+atrist["name"]+" Song - "+track["name"]+"</h1>"+"</div>"+
               map.get_root().render())
