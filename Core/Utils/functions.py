import toml


def load_toml(file: str) -> dict:
    """Load toml content from the given file"""
    with open(file, encoding="utf-8") as newfile:
        return toml.load(newfile)
