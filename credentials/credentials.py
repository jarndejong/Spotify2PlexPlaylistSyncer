"""
This module loads .yaml configurations as dictionaries.
"""
import yaml

def load_configuration(path: str):
    """
    Load a .yaml configuration from file as a docstring.
    """
    with open(path, "r", encoding = "utf-8") as f:
        return yaml.safe_load(f)


spotify = load_configuration("./credentials/spotify.yaml")
plex = load_configuration("./credentials/plex.yaml")
