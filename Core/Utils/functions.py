import json
import toml


def load_json(file: str) -> dict:
    """ Load json content from the given file """
    with open(file, encoding = 'utf-8') as newfile:
        return json.load(newfile)


def write_json(file: str, contents: dict) -> None:
    """ Write json content on to the given file """
    with open(file, 'w') as newfile:
        json.dump(contents, newfile, ensure_ascii = True, indent = 4)

def load_toml(file: str) -> dict:
    """ Load toml content from the given file """
    with open(file, encoding = 'utf-8') as newfile:
        return toml.load(newfile)


def write_toml(file: str, contents: dict) -> None:
    """ Write toml content on to the given file """
    with open(file, 'w') as newfile:
        toml.dump(contents, newfile)

def _size(num):
    """ Convert Size from Bytes to appropriate size."""
    for unit in ['B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB']:
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}YB"
            
def _bitsize(num):
    """ Convert from Bytes to appropriate size."""
    for unit in ['B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB']:
        if abs(num) < 1000.0:
            return f"{num:.1f}{unit}"
        num /= 1000.0
    return f"{num:.1f}YB"