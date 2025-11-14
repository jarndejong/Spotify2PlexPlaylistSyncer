"""
This module loads settings.yaml as a dictionary.
"""
from credentials.credentials import load_configuration

settings = load_configuration('./settings.yaml')
settings['mapping_dict'] = None
# Add the mapping dictionary to the settings if it exists.
if settings['mapping_file']:
    settings['mapping_dict'] = load_configuration(settings['mapping_file'])
if settings['skip_file']:
    settings['skips'] = load_configuration(settings['skip_file'])['skips']