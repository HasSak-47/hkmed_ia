from typing import List
from requests import request

from scraper.utils import DOMAIN


def __rx_class(path: str, **kwargs):
    url = f'{DOMAIN}/REST/rxclass/{path}.json'
    r = request('GET', url, params=kwargs if kwargs else None)
    if r.status_code != 200:
        return None
    return r.json()

def get_all_classes(classTypes: List[str] | None):
    """
    Get all classes, or classes of certain types (the classTypes parameter).
    """
    ty = None
    if classTypes is not None:
        ty = ''.join(classTypes)
    return __rx_class("allClasses", classTypes=ty)


def get_class_types() -> List[str] | None:
    """
    Get the class types. The resources findClassByName, getClassTree, getClassGraphBySource, and getAllClasses use the class types as filters for the output. 
    """
    tys = __rx_class("classTypes")
    if tys is None:
        return None

    return tys['classTypeList']['classTypeName']

def populate_class_types():
    types = get_class_types()
    if types is None:
        raise RuntimeError("failed to get types")

    s = 'TYPES : List[str] = [' + ''.join([f'"{ty}", ' for ty in types]) + ']'
    with open('scrapper/generated/rx_classes.py', 'w+') as file:
        file.write('from typing import List\n')
        file.write(s)
