import yaml

def load_configuration(path: str) -> dict:
    with open(path, "r", encoding = 'utf-8') as f:
        return yaml.safe_load(f)

settings = load_configuration('./settings.yaml')
settings['mapping_dict'] = None
if settings['mapping_file']:
    settings['mapping_dict'] = load_configuration(settings['mapping_file'])