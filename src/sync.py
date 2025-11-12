
from plexapi.library import MusicSection
from plexapi.playlist import Playlist
from plexapi.audio import Track
from plexapi.exceptions import NotFound

from src.matching import link_track
from src.spotify import tracks_from_spotify_playlist
from src.plex import library, get_plex_playlist_name

def sync(settings: dict[str,str | list[str] | bool]):
    '''
    Sync/create playlist based on settings.
    '''
    # Check typing
    assert isinstance(settings['playlist_id'], str)
    assert isinstance(settings['matching_pattern'], (str, list))
    assert isinstance(settings['print_matching_status'], bool)
    assert isinstance(settings['mapping_dict'], dict)

    spotify_tracks = tracks_from_spotify_playlist(settings['playlist_id'])

    matched, unmatched, plex_tracks = find_tracks(plexlibrary = library,
                              spotify_tracks = spotify_tracks,
                              matching_pattern = settings['matching_pattern'],
                              print_status = settings['print_matching_status'],
                              mapping_dict = settings['mapping_dict'])

    playlist_name = get_plex_playlist_name()

    if settings['dry_run']:
        return matched, unmatched, plex_tracks
    if settings['sync_mode'] == 'from_scratch':
        create_playlist(plexlibrary = library,
                        plex_tracks = plex_tracks,
                        playlist_name = playlist_name)
        return matched, unmatched, plex_tracks
    if settings['sync_mode'] == 'append':
        raise NotImplementedError("This sync mode has not yet been implemented.")
    elif settings['sync_mode'] == 'append':
        raise NotImplementedError("This sync mode has not yet been implemented.")
    else:
        raise ValueError(f"Sync mode {settings['sync_mode']} is not known, valid options are from_scratch, append, append_new. Please check settings.yaml.")

def create_playlist(plexlibrary: MusicSection, plex_tracks: list[Track], playlist_name: str):
    '''
    Create a new playlist with the given name containing the given tracks.
    This is irrespective of if there already is a playlist with the given name.
    '''
    return plexlibrary.createPlaylist(title = playlist_name,
                               items = plex_tracks,
                               smart = False,
                               )

def append_playlist(plexlibrary: MusicSection, plex_tracks: list, playlist_name: str):
    '''
    Append the given tracks to the given playlist. Raises ValueError if no such playlists exists.
    '''
    try:
        playlist = plexlibrary.playlist(playlist_name)
    except NotFound as exc:
        raise ValueError(f"Can't find playlist named {playlist_name}, available playlists:\n{'\t\'n'.join([playlist.title for playlist in plexlibrary.playlists()])}") from exc
    assert isinstance(playlist, Playlist)
    playlist.addItems(plex_tracks)

def append_playlist_newtracks_only(plexlibrary: MusicSection,
                                   plex_tracks: list,
                                   playlist_name: str):
    '''
    Append the given tracks to the given playlist, but only if the tracks are not in there yet. Raises ValueError if no such playlists exists.
    '''
    try:
        playlist = plexlibrary.playlist(playlist_name)
    except NotFound as exc:
        raise ValueError(f"Can't find playlist named {playlist_name}, available playlists:\n{'\t\'n'.join([playlist.title for playlist in plexlibrary.playlists()])}") from exc
    assert isinstance(playlist, Playlist)
    current_track_ids = [track.ratingKey for track in playlist.items()]
    new_tracks = []
    for track in plex_tracks:
        if not track.ratingKey in current_track_ids:
            new_tracks.append(track)
    playlist.addItems(new_tracks)

def find_tracks(plexlibrary: MusicSection,
                spotify_tracks: list[dict[str, str | list[str]]],
                matching_pattern: str | list[str],
                print_status: bool = False,
                mapping_dict: dict[str,str] | None = None) -> tuple[list[dict], list[dict], list[Track]]:
    '''
    Try to match all the tracks in the spotify_tracks list with songs in the plexlibrary music library.
    '''
    matched = []
    unmatched = []
    found = []

    nr_spotify_tracks = len(spotify_tracks)
    for nr, element in enumerate(spotify_tracks):
        if print_status:
            print(f"At track nr {nr+1}/{nr_spotify_tracks}")
        
        spotify_track = element['track'] # type: ignore
        spotify_track_name = spotify_track['name'] # type: ignore
        # Check typing
        assert isinstance(spotify_track, dict)

        plex_track = link_track(plexlibrary=plexlibrary,
                                spotify_track = spotify_track,
                                mapping_dict = mapping_dict,
                                matching_strength=matching_pattern)

        if plex_track:
            if print_status:
                print(f"\tMatched spotify track {spotify_track_name} as plex track {plex_track.title}")
            matched.append(element)
            found.append(plex_track)
        else:
            if print_status:
                print(f"\tCould not find match for spotify track {spotify_track_name}")
            unmatched.append(element)
    return matched, unmatched, found