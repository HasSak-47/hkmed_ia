from typing import List
from scraper.utils import rx_class


def get_all_classes(classTypes: List[str] | None):
    """
    Get all classes, or classes of certain types (the classTypes parameter).
    """
    ty = None
    if classTypes is not None:
        ty = ''.join(classTypes)
    return rx_class("allClasses", classTypes=ty)

def get_class_types():
    """
    Get the class types. The resources findClassByName, getClassTree, getClassGraphBySource, and getAllClasses use the class types as filters for the output. 
    """
    return rx_class("classTypes")
