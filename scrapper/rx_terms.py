# see https://lhncbc.nlm.nih.gov/RxNav/APIs/RxTermsAPIs.html
from typing import List, Optional
from requests import request
from sys import argv

from .utils import DOMAIN

def __rx_terms(path: str, **kwargs):
    """Internal helper function to make API requests"""
    url = f'{DOMAIN}/REST/RxTerms/{path}.json'
    r = request('GET', url, params=kwargs if kwargs else None)
    if r.status_code != 200:
        return None
    return r.json()

def get_all_concepts():
    """
    not implemented
    """
    raise RuntimeError('not implemented')

def get_all_rx_term_info(*_):
    """
    not implemented
    """
    raise RuntimeError('not implemented')

def get_rx_term_display_name(*_):
    """
    not implemented
    """
    raise RuntimeError('not implemented')

def get_rx_terms_version(*_):
    """
    not implemented
    """
    raise RuntimeError('not implemented')
