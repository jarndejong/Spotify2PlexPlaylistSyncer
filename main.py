#%%
from settings import settings
from src.sync import sync
from src.save import handle_savetodisk

#%%
matched, unmatched, plex_tracks, skipped = sync(settings)


print(f"\t{len(matched)} matched, {len(unmatched)} unmatched and {len(skipped)} skipped tracks.")

handle_savetodisk(unmatched, matched, plex_tracks, settings)
