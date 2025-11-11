from rapidfuzz import fuzz, process
from typing import cast, Sequence
import re
import unicodedata
from plexapi.library import MusicSection
from plexapi.audio import Track, Album

def search_track(plexlibrary: MusicSection, spotify_track: dict[str,str|dict|list], matching_strength: str | list[str]) -> Track | None:
    '''
    Search for a match with the given spotify track in the plex library.
    The settings determine how strict the matching is.
    '''
    if isinstance(matching_strength, list):
        found_track = None
        for strength in matching_strength:
            found_track = search_track(plexlibrary = plexlibrary, spotify_track = spotify_track, matching_strength = strength)
        return found_track
    if matching_strength == 'exact':
        return _search_track_exact(plexlibrary, spotify_track)
    elif matching_strength == 'strict':
        return _search_track_strict(plexlibrary, spotify_track)
    elif matching_strength == 'loose':
        return _search_track_loose(plexlibrary, spotify_track)
    elif matching_strength == 'artist':
        return _search_track_by_artist(plexlibrary, spotify_track)
    elif matching_strength == 'artistfuzzy':
        return _search_track_by_artist(plexlibrary, spotify_track, fuzzymatch = True)
    elif matching_strength == 'album':
        return _search_track_by_album(plexlibrary, spotify_track)
    elif matching_strength == 'albumartist':
        return _search_track_by_album_and_artist(plexlibrary, spotify_track)
    elif matching_strength == 'descending':
            return search_track(plexlibrary = plexlibrary, spotify_track = spotify_track, matching_strength = ['exact', 'strict', 'albumartist', 'album' , 'artist', 'loose'])
    else:
        raise ValueError(f"Matching setting {matching_strength} is unknown, available values are:\n\t exact, strict, loose, album, albumartist, descending")
    

def _clean_title(title: str) -> str:
    """Clean Spotify or Plex track/album titles for fuzzy matching."""
    if not isinstance(title, str):
        return ""
        
    # Normalize Unicode (accents, dashes, etc.)
    title = unicodedata.normalize("NFKD", title)

    # Lowercase for consistency
    title = title.lower()

    # Remove common suffixes after a dash, like " - remastered 2008", " - edit", " - mono lp version"
    title = re.sub(
        r"\s*-\s*(remaster(ed)?(\s*\d{4})?|mono|stereo|single|album|radio|"
        r"bonus|lp|version|mix|edit|take|alt|acoustic|live|reissue)\b.*",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Remove parenthetical metadata like "(Remastered)", "(Deluxe Edition)", "(Bonus Track)", "(Single Version)"
    title = re.sub(
        r"\s*\(([^)]*(remaster|deluxe|bonus|version|mix|edit|take|acoustic|mono|stereo|live|album|radio)[^)]*)\)",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Remove trailing album references like "(from ...)" or "(...) version"
    title = re.sub(r"\s*\(from [^)]*\)", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*\(.*?version\)", "", title, flags=re.IGNORECASE)

    # Remove redundant punctuation and multiple spaces
    title = re.sub(r"[\[\]\(\)]", "", title)
    title = re.sub(r"\s{2,}", " ", title)

    # Strip punctuation at ends
    title = title.strip(" -_.")

    return title.strip()

def _search_track_exact(plexlibrary: MusicSection, spotify_track:  dict) -> Track | None:
    '''
    Search the plex library for a given track based on the exact song title, artist name and album title.
    This includes titles with e.g. 'Remastered edition' etc., so the overlap has to be exact.
    '''
    track_name = spotify_track['name']

    artists = spotify_track['artists']
    artist_name = artists[0]['name']

    spotify_album_name = spotify_track['album']['name']

    filters = {
        "artist.title": artist_name,
        "album.title": spotify_album_name,
               }

    found_tracks = plexlibrary.searchTracks(title = track_name,
                                        filters = filters,
                         )
    if found_tracks:
        return found_tracks[0]
    else:
         return None

def _search_track_strict(plexlibrary: MusicSection, spotify_track: dict) -> Track | None:
    '''
    Search the plex library for a given track based on the song title and artist name.
    Returns a track if the album title also aligns, otherwise returns None.
    '''
    track_name = _clean_title(spotify_track['name'])

    artists = spotify_track['artists']
    artist_name = _clean_title(artists[0]['name'])

    spotify_album_name = _clean_title(spotify_track['album']['name'])

    filters = {
        "artist.title": artist_name,
        "album.title": spotify_album_name,
               }

    found_tracks = plexlibrary.searchTracks(title = track_name,
                                        filters = filters,
                         )

    for found in found_tracks:
        if fuzz.partial_ratio(spotify_album_name, _clean_title(found.album().title)) > 0.8:
            return found
    
    return None

def _search_track_by_artist(plexlibrary: MusicSection, spotify_track: dict, fuzzymatch = False) -> Track | None:
    '''
    Search the plex library for a given track by first searching for the artist.
    If an artist is found, returns a track if the artist has a track that aligns with the track name (either with fuzzy logic or not). Otherwise returns None.

    '''
    spotify_track_name = _clean_title(spotify_track['name'])

    artists = spotify_track['artists']
    spotify_artist_name = _clean_title(artists[0]['name'])

    found_artists = plexlibrary.searchArtists(title = spotify_artist_name)

    matched_artist = None
    for found_artist in found_artists:
        if fuzzymatch:
            if fuzz.partial_ratio(spotify_artist_name, _clean_title(found_artist.title)) > 80:
                matched_artist = found_artist
                continue
        else:
            if spotify_artist_name == _clean_title(found_artist.artist().title):
                matched_artist = found_artist
                continue
    
    if matched_artist:
        for plex_track in matched_artist.tracks():
            if fuzzymatch:
                if fuzz.partial_ratio(spotify_track_name, _clean_title(plex_track.title)) > 80:
                    return plex_track
            else:
                if spotify_track_name == _clean_title(plex_track.title):
                    return plex_track

    return None

def _search_track_by_album_and_artist(plexlibrary: MusicSection, spotify_track: dict) -> Track | None:
    '''
    Search the plex library for a given track by first searching for its album & artist.
    Uses fuzzy logic to find best match when multiple albums are found.
    Returns the track if the album can be found and if there is a song that aligns.
    '''
    track_name = _clean_title(spotify_track['name'])
    artist_name = _clean_title(spotify_track['artists'][0]['name'])
    album_name = _clean_title(spotify_track['album']['name'])

    found_albums = plexlibrary.searchAlbums(title = album_name, filters = {'artist.title': artist_name}) # type: list[Album]

    found_album, score = None, 0
    for plex_album in found_albums:
        match_score = fuzz.partial_ratio(plex_album.title, album_name)
        if match_score > score:
            score = match_score
            found_album = plex_album # type: Album | None
    
    # If an album is found, search for the song.
    if found_album:
        album_tracks = cast(Sequence[Track], found_album.tracks())
        for plex_track in album_tracks:
            assert isinstance(plex_track, Track)
            if fuzz.partial_ratio(_clean_title(plex_track.title), track_name) > 80:
                return plex_track
    
    return None

def _search_track_by_album(plexlibrary: MusicSection, spotify_track: dict) -> Track | None:
    '''
    Search the plex library for a given track by first searching for its album.
    Uses fuzzy logic to find best match when multiple albums are found.
    Returns the track if the album can be found and if there is a song that aligns.
    '''
    track_name = _clean_title(spotify_track['name'])
    artist_name = _clean_title(spotify_track['artists'][0]['name'])
    album_name = _clean_title(spotify_track['album']['name'])

    found_albums = plexlibrary.searchAlbums(title = album_name) # type: list[Album]

    found_album, score = None, 0
    for plex_album in found_albums:
        plex_artist = plex_album.artist()
        assert plex_artist
        plex_artist_name = plex_artist.title # type: str
        match_score = fuzz.partial_ratio(_clean_title(plex_album.title), album_name) + fuzz.partial_ratio(_clean_title(plex_artist_name), artist_name)
        if match_score > score:
            score = match_score
            found_album = plex_album # type: Album | None
    
    # If an album is found, search for the song.
    if found_album:
        album_tracks = cast(Sequence[Track], found_album.tracks())
        for plex_track in album_tracks:
            assert isinstance(plex_track, Track)
            if fuzz.partial_ratio(_clean_title(plex_track.title), track_name) > 80:
                return plex_track
    
    return None

def _search_track_loose(plexlibrary: MusicSection, spotify_track: dict) -> Track | None:
    '''
    Search the plex library for a given track based on the song title.
    If multiple tracks are found, returns the one with the highest fuzzy logic score.
    Returns a track if the album title also align, otherwise returns None.
    '''
    track_name = _clean_title(spotify_track['name'])

    artists = spotify_track['artists']
    spotify_artist_name = _clean_title(artists[0]['name'])

    spotify_album_name = _clean_title(spotify_track['album']['name'])

    found_tracks = plexlibrary.searchTracks(title = track_name,
                         )

    score = 0
    plex_track = None
    for found_track in found_tracks:
        match_score = fuzz.partial_ratio(spotify_artist_name, _clean_title(found_track.artist().title))
        match_score += 0.2*fuzz.partial_ratio(spotify_album_name, _clean_title(found_track.album().title))
        if match_score > score:
            score = match_score
            plex_track = found_track
    
    return plex_track