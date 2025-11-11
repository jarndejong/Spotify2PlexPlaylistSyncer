#%%

from settings import settings
from src.sync import sync
from src.save import save_unmatched, save_matched

matched, unmatched, plex_tracks = sync(settings)

print(f"Number of unmatched tracks: {len(unmatched)}")

if settings['print_unmatched_to_file']:
    save_unmatched(unmatched = unmatched, 
                   settings = settings)

if settings['print_matched_to_file']:
    save_matched(matched = matched,
                 found = plex_tracks,
                 settings = settings)

