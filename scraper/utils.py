from typing import Final
from requests import request

DOMAIN : Final = "https://rxnav.nlm.nih.gov"

def rx_class(path: str, **kwargs):
    url = f'{DOMAIN}/REST/rxclass/{path}.json'
    r = request('GET', url, params=kwargs if kwargs else None)
    if r.status_code != 200:
        return None
    return r.json()


def rx_terms(path: str, **kwargs):
    url = f'{DOMAIN}/REST/RxTerms/{path}.json'
    r = request('GET', url, params=kwargs if kwargs else None)
    if r.status_code != 200:
        return None
    return r.json()
