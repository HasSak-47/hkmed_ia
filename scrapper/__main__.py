from sys import argv
from . import rx_class 
from pprint import pprint as pp

def main():
    pp(rx_class.get_classes_by_id('N0000000133'))
    pass

if __name__ == "__main__":
    main()
