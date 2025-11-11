import yaml

def load_configuration(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

settings = load_configuration('./settings.yaml')