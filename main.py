# Import libraries
from bs4 import BeautifulSoup
from functools import reduce
import requests
import codecs
import json


def getLower(input: str) -> str:
    ''' Lowers the input including Turkish characters '''
    # Map
    d = {
        "Ş": "ş", "I": "ı", "Ü": "ü",
        "Ç": "ç", "Ö": "ö", "Ğ": "ğ",
        "İ": "i", "Â": "â", "Î": "î",
        "Û": "û"
    }
    # Replace
    input = reduce(lambda x, y: x.replace(y, d[y]), d, input)
    # Lower the input
    input = input.lower()

    #: Return
    return input


def readTextFile(filename: str):
    with codecs.open(filename, encoding='utf-8') as f:
        for line in f:
            line = line.strip('\n').strip('\r')
            if len(line) > 0:
                yield line
    #: Close
    f.close()


def readJSON(filename: str) -> dict:
    # Open file
    with open(filename) as f:
        # Return json
        return json.load(f)


def writeJSON(data: dict, filename: str):
    # Open file
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        # Dump JSON file
        json.dump(data, f, ensure_ascii=False, indent=4)
