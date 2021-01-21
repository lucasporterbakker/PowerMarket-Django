from urllib.parse import quote_plus


def slug_from_address(address):
    return quote_plus(address)
