#%%
from settings import settings
from src.sync import sync
from src.save import handle_savetodisk

#%%
matched, unmatched, plex_tracks = sync(settings)

print(f"Number of unmatched tracks: {len(unmatched)}")

handle_savetodisk(unmatched, matched, plex_tracks, settings)
