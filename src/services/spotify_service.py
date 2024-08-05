import requests
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("SPOTIFY_TOKEN")




# Authorization token that must have been created previously. See: https://developer.spotify.com/documentation/web-api/concepts/authorization

def fetch_web_api(endpoint, method, body=None):
    url = f"https://api.spotify.com/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.request(method, url, headers=headers, json=body)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    return response.json()

def get_top_tracks():
    # Endpoint reference: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    endpoint = 'v1/me/top/tracks?time_range=long_term&limit=5'
    return fetch_web_api(endpoint, 'GET')['items']

if __name__ == "__main__":
    try:
        top_tracks = get_top_tracks()
        for track in top_tracks:
            name = track['name']
            artists = ', '.join(artist['name'] for artist in track['artists'])
            print(f"{name} by {artists}")
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
