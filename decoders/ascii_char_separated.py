def decode(raw_data: bytes, config: dict) -> list:
    return raw_data.decode('ascii').split(config['separator'])
