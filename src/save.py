from plexapi.audio import Track

def save_unmatched(unmatched: list[dict[str,str | list]], settings: dict[str, str | list[str]]):
    '''
    Save the unmatched Spotify songs to file.
    '''
    raise NotImplementedError("Saving to file is not yet implemented, please change in settings.yaml")

def save_matched(matched: list[dict[str, str | list[str]]], found: list[Track], settings: dict[str, str | list[str]]):
    '''
    Save the matched Spotify songs and their Plex tracks to file.
    '''
    raise NotImplementedError("Saving to file is not yet implemented, please change in settings.yaml")