"""
This module handles all Plex API interactions.
"""
from plexapi.server import PlexServer
from plexapi.exceptions import NotFound, Unauthorized

from src.spotify import get_spotify_playlist_name
from credentials.credentials import plex as plcredentials
from settings import settings

try:
    plex = PlexServer(plcredentials["baseurl"], plcredentials["token"])
except NotFound as exc:
    raise ValueError(f"Could not find plex server at {plcredentials["baseurl"]}, please check the settings.") from exc
except Unauthorized as exc:
    raise ValueError(f"Could not access plex server with token {plcredentials["token"]}, please check the settings.") from exc

try:
    library = plex.library.section(settings["plex_library_name"])
except NotFound as exc:
    available_libraries = [library.title for library in plex.library.sections() if library.TYPE == "artist"]
    raise NotFound(f"Could not find the library {settings["plex_library_name"]}. Available libraries:" + "\n\t".join(available_libraries)) from exc

def get_plex_playlist_name() -> str:
    '''
    Get the name for the plex playlist. This is retrieved from the settings.
    '''
    playlist_name = settings['plex_playlist_name']
    if playlist_name is None:
        playlist_name = get_spotify_playlist_name(settings["playlist_id"])
    
    assert playlist_name is not None
    return playlist_name