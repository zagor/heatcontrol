import json
from threading import Lock
from typing import Dict

_config = {}
_config_mutex = Lock()


def _load():
    with _config_mutex:
        try:
            with open('config.json') as f:
                global _config
                _config = json.load(f)
        except FileNotFoundError:
            pass


def _save():
    with _config_mutex:
        with open('config.json', 'w') as f:
            json.dump(_config, f, sort_keys=True, ensure_ascii=True, indent=2)


def get(name):
    with _config_mutex:
        return _config.get(name)


def put(name, value):
    with _config_mutex:
        _config[name] = value
    _save()


def put_defaults(defaults: Dict):
    for key, value in defaults.items():
        if not get(key):
            put(key, value)


def init():
    _load()

