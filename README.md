# Spotify2PlexPlaylistSyncer
A straightforward tool to sync a Spotify playlist to a Plex playlist.

## TL/DR
- Provide `credentials/plex.yaml` and `credentials/spotify.yaml`
- Fill in `settings.yaml`
- Install requirements (`requirements.txt`)
- run `main.py`
- (Optional) check `unmatched_tracks.csv`

## Installation
Clone this repository & change into:
```
cd https://github.com/jarndejong/Spotify2PlexPlaylistSyncer.git
git clone url
cd Spotify2PlexPlaylistSyncer
```

It is advisable to create a virtual python environment before installing the requirements
```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Setup credentials
You need credentials/API tokens to access both Spotify and your plex instance.
#### Setup spotify
Rename `credentials/example.spotify.yaml` to `credentials/spotify.yaml`. 

You need to create your [own spotify API application](https://developer.spotify.com/) as explained [here](https://pypi.org/project/spotipy/#installation) and then provide:
- client_id
- client_secret
- redirect_uri

Upon the first run, python will open your browser. You will need to copy the url into the terminal.

#### Setup plex
Rename `credentials/example.plex.yaml` to `credentials/plex.yaml`. 

For plex you just need to provide:
- The URL where your plex server is accessible. This can be e.g. `http://ip-address:32400` if you're not using a reverse proxy/not exposing your plex server beyond your network.
- An API token to your plex server, [as described here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

## Running the script
First, create settings as described below.
Then run the script as:
```
.venv/bin/python -m main.py
```

Alternatively, you can use the following functions in your own scripts.
Main sync:
```
from settings import settings
from src.sync import sync
matched, unmatched, plex_tracks = sync(settings)
```
Saving matched and unmatched to file:
```
from src.save import save_unmatched, save_matched
save_unmatched(unmatched = unmatched, settings = settings)
save_matched(matched = matched, found = plex_tracks, settings = settings)
```


## Setup the script
Rename `example.settings.yaml` to `settings.yaml`.
A quick overview of the settings is as follows:
### Playlist settings
##### `playlist_id:`
Either the playlist id, or the full playlist url (spotify -> playlist -> share -> copy link to playlist).

##### `plex_library_name:`
Name of the Plex music library to search for tracks and create the playlist in.

##### `plex_playlist_name:`
Name of the playlist that will be created or synced to in Plex.
If `false` or nothing, the name of the spotify playlist will be used.

##### `dry_run:`
Either `true` or `false`. If `true`, skip creating the playlist. The matched & unmatched tracks are still written to fiel (see below).

### Sync settings
##### `sync_mode:`
Type of sync. Options are:
- `append`: Append all matched tracks from the spotify playlist to the plex playlist.
- `append_new`: Append only those matched tracks from the spotify playlist to the plex playlist that are not already in there.
- `from_scratch`: Create a new plex playlist with the matched spotify tracks.

##### `create_new_plex_playlist:`
Either `true` or `false`. If `true`, create a new playlist if the to-be-sycned playlist cannot be found for `sync_mode: append` or `sync_mode: append_new`. Does nothing for `sync_mode: from_scratch`.

### Matching settings
##### `matching_pattern:`
What type of matching to use. Options are:
- `exact`: Exact matching for title, artist and album. e.g. the Spotify track `Here Comes The Sun - Remastered 2009` will not be matched with a Plex songs that is titled just `Here Comes The Sun`.
- `strict`:  Essentially the same as exact matching, but will try to clean up track title, album title and artist name first. Cleanup is done by regex filters; all other options below also use cleanup.
- `loose`: First searches the plex library only based on the song title. Then loops through all found tracks and uses weighted fuzzy logic to find the best match based on artist name (weight 1), and partly on album name (weight 0.2).
- `artist`: First searches the plex library for the artist. Then searches to the tracks of those artist to find a match based on song title.
- `artistfuzzy`: Same as `artist` but uses fuzzy logic to match the songs.
- `album`: First searches the plex library for the album. Then loops through all found albums and uses fuzzy logic to match the artist. If an album match is found, loops through its tracks and uses fuzzy logic to match the tracks.
- `albumartist`:  Like `album`, but the album search is performed with the artist name as metadata.
- `descending`: special settings that loops through the other settings in following order: `'exact', 'strict', 'albumartist', 'album' , 'artist', 'loose'`, until a match is found.

Alternatively, a list of these options can be provided, which will be used iteratively until a match is found.

##### `print_matching_status:`
Either `true` or `false`. If `true`, print the matching status of every spotify track (i.e. whether a match was found).

##### `mapping_file:`
Optionally, you can provide a dictionary (as `.yaml`) that maps Spotify track IDs to Plex track IDs. 
This hardcodes a matching for any Spotify track that is in the dictionary to a given Plex track. 
Any song in the Spotify playlist that is not hardcoded will be searched for.

An example is given in `example.hardcoded_matches/example.yaml`.

Spotify track ID's can be retrieved from their URL. Additionally, the unmatched and matched tracks overview files (see below) will contain the track ID's.

Plex ID's can be found e.g. by [inspecting the XML](https://support.plex.tv/articles/201998867-investigate-media-information-and-formats/).
If `false` or nothing, all tracks will be linked through standard search attempts.

##### `skip_file:`
Optionally, you can provide a list (as `.yaml`, see example in `example.hardcoded_matches/skip.yaml`) of Spotify ID's to skip.
This is especially useful if you are certain no match exists in your Plex library.

### Miscellaneous
##### `print_unmatched_to_file:`
Either `true` or `false`. If `true`, the unmatched spotify tracks will be printed to file.
##### `unmatched_tracks_filename:`
Relative filename of the unmatched tracks file. Can be either a `.txt` or `.csv` file.

##### `print_matched_to_file:`
Either `true` or `false`. If `true`, the matched spotify tracks and plex tracks will be printed to file. For error checking etc.
##### `matched_tracks_filename:`
Relative filename of the matched tracks file. Can be either a `.txt` or `.csv` file.

##### `create_hardcoded_mapping:`
Either `true` or `false`. If true, save a mapping dictionary to a yaml file for all the matched tracks.
##### `mapping_file_savepath:`
Filepath where to save, e.g. `hardcoded_matches/dryrun.yaml`

# Online repository
The publicly available repository on GitHub (i.e. available [here](https://github.com/jarndejong/Spotify2PlexPlaylistSyncer); most likely you are currently viewing this one) is an automated mirror from a private, self-hosted git repository.