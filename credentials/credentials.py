import yaml

def load_configuration(path="settings.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


spotify = load_configuration("./credentials/spotify.yaml")
plex = load_configuration("./credentials/plex.yaml")