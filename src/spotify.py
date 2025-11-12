"""
This module handles all Spotify API interactions.
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from credentials.credentials import spotify as spcredentials


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spcredentials["client_id"],
    client_secret=spcredentials["client_secret"],
    redirect_uri=spcredentials["redirect_uri"],
    scope=spcredentials["scope"],
))

def get_spotify_playlist_name(playlist_id: str) -> str:
    '''
    Retrieve the spotify playlist name from the id.
    '''
    try:
        playlist = sp.playlist(playlist_id)
        assert playlist is not None
        return playlist['name']
    except SpotifyException as exc:
        raise ValueError(f"Could not retrieve spotify playlist with id {playlist_id}, please check the settings.") from exc

def tracks_from_spotify_playlist(playlist_id: str) -> list[dict[str, str|list[str]]]:
    '''
    Get a list of all tracks in a Spotify playlist by id.
    '''
    tracks = []
    results = sp.playlist_items(playlist_id, limit = 100) # type: dict[str, str | list] | None
    assert results is not None
    
    tracks.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        assert results is not None
        tracks.extend(results["items"])
    
    return tracks