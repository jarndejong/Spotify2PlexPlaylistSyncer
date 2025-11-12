import csv
from plexapi.audio import Track


def save_unmatched(unmatched: list[dict[str,str | list]], settings: dict[str, str | list[str]]):
    '''
    Save the unmatched Spotify songs to file. The file type and path will be inferred from the given settings.
    '''
    if settings['unmatched_tracks_filename'].endswith('.txt'):
        _save_unmatched_to_txt(unmatched, settings['unmatched_tracks_filename'])
    elif settings['unmatched_tracks_filename'].endswith('.csv'):
        _save_unmatched_to_csv(unmatched, settings['unmatched_tracks_filename'])
    else:
        raise ValueError(f"{settings['unmatched_tracks_filename']} is not a .txt or .csv file.")

def _save_unmatched_to_txt(unmatched: list[dict[str,str | list]], filepath: str):
    '''
    Save the unmatched tracks to a .txt file.
    '''
    with open(filepath, 'w', encoding = "utf-8") as fh:
        width = len(str(len(unmatched)))
        for nr, element in enumerate(unmatched, start = 1):
            spotify_artist = element['track']['artists'][0]['name']
            spotify_name = element['track']['name']
            spotify_album = element['track']['album']['name']
            spotify_track_id = element["track"]['id']
            fh.write(f"{nr:>{width}}: {spotify_artist} -- {spotify_name} ({spotify_album}) [{spotify_track_id}]\n")

def _save_unmatched_to_csv(unmatched: list[dict[str,str | list]], filepath: str):
    '''
    Save the unmatched tracks to a .csv file.
    '''
    with open(filepath, 'w', newline="", encoding = "utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Artist", "Title", "Album", "Spotify ID"])
        writer.writerows([
                (
                    spotify_element["track"]["artists"][0]["name"],
                    spotify_element["track"]["name"],
                    spotify_element["track"]["album"]["name"],
                    spotify_element["track"]["id"],
                )
                for spotify_element in unmatched
                ])

def save_matched(matched: list[dict[str, str | list[str]]], found: list[Track], settings: dict[str, str | list[str]]):
    '''
    Save the matched Spotify songs and their Plex tracks to file.
    '''
    if settings['matched_tracks_filename'].endswith('.txt'):
        _save_matched_to_txt(matched, found, settings['matched_tracks_filename'])
    elif settings['matched_tracks_filename'].endswith('.csv'):
        _save_matched_to_csv(matched, found, settings['matched_tracks_filename'])
    else:
        raise ValueError(f"{settings['unmatched_tracks_filename']} is not a .txt or .csv file.")
    
def _save_matched_to_txt(matched: list[dict[str, str | list[str]]], found: list[Track], filepath: str):
    '''
    Save the matched tracks to a .txt file.
    '''
    with open(filepath, 'w', encoding = "utf-8") as fh:
        width = len(str(len(matched)))
        for nr, [spotify_element, plex_track] in enumerate(zip(matched, found), start = 1):
            spotify_artist = spotify_element['track']['artists'][0]['name']
            spotify_name = spotify_element['track']['name']
            spotify_album = spotify_element['track']['album']['name']
            spotify_track_id = spotify_element["track"]['id']
            plex_artist = plex_track.artist().title
            plex_name = plex_track.title
            plex_album = plex_track.album().title
            plex_track_id = plex_track.ratingKey
            fh.write(f"\n{nr:>{width}}: {spotify_name} -- {plex_name} ({spotify_artist} ({spotify_album}) -- {plex_artist} ({plex_album})) [{spotify_track_id} -- {plex_track_id}]\n")

def _save_matched_to_csv(matched: list[dict[str, str | list[str]]], found: list[Track], filepath: str):
    '''
    Save the matched tracks to a .csv file.
    '''
    with open(filepath, 'w', newline="", encoding = "utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Spotify Artist", "Spotify Title", "Plex Artist", "Plex Title", "Spotify ID", "Plex ID"])
        writer.writerows([
                (
                    spotify_element["track"]["artists"][0]["name"],
                    spotify_element["track"]["name"],
                    plex_track.artist().title,
                    plex_track.title,
                    spotify_element["track"]["id"],
                    plex_track.ratingKey,
                )
                for spotify_element, plex_track in zip(matched, found)
                ])
def save_hardcoded_matching(spotify_tracks: list[dict[str, str | list[str]]], plex_tracks: list[Track], settings: dict[str, str | list[str]]):
    '''
    Create a hardcoded matching file, that links specific spotify tracks to specific plex tracks by ID.
    '''
    with open(settings['mapping_file'], 'w', newline="", encoding = "utf-8") as fh:
        for spotify_track, plex_track in zip(spotify_tracks, plex_tracks):
            comment = f" # {plex_track.artist().title} — {plex_track.title}\n"
            fh.write(f"{spotify_track['track']['id']}: {plex_track.ratingKey}{comment}")