import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"
# scope = 'user-modify-playback-state'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_saved_tracks():
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])