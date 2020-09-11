# Import libraries
from collections import defaultdict
from bs4 import BeautifulSoup
from functools import reduce
from numpy import random
import pandas as pd
import requests
import codecs
import json
import sys


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


def calc_prob_dist(d: dict) -> list:
    # Declare an empty list
    t_showns = list()
    # Declare words
    words = d.keys()
    # Iterate through words of dict
    for word in words:
        # Append how many times it is shown variable
        t_showns.append(d[word]['times_shown'])
    # Create a frame of words and the number of exhibitions
    df = pd.DataFrame(data=zip(words, t_showns), columns=['words', 'times_shown'])
    # Create a new frame which is sorted by times_shown column
    df2 = df.sort_values(by='times_shown', ascending=True)
    # Add an additional column of values which are ascending=False to df2
    df2['desc_times_shown'] = df2.sort_values(
        by='times_shown', ascending=False
    ).times_shown.to_numpy()
    # Calculate the total number in times_shown column
    total = df.times_shown.sum()
    # Calculate the probabilities
    df2['probs'] = df2.desc_times_shown.apply(lambda x: x / total)

    # Return words list and probability distribution
    return df2.words.to_numpy(), df2.probs.to_numpy()


# Declare URLs to request
URL_LEX = 'https://www.lexico.com/definition/'
URL_TUR = 'https://tureng.com/en/turkish-english/'

# Read files
d = readJSON('dict.json')  # JSON file

# If -update arg is received
if sys.argv[1] == '-update':
    # Iterate through words
    for idx, word in enumerate(readTextFile('inp.txt')):
        # If word not in dict.json
        if word not in d:
            # Try finding missing words' meanings
            try:
                # Trace
                print(f'Handling {word}, line: {idx}')
                # Setup within key in dictionary
                d[word] = defaultdict(list, {
                    'English': {}, 'Turkish': list(), 'times_shown': 1
                })
                # Read Lexico website
                lexico = requests.get(URL_LEX + word).text
                # Create BeautifulSoup obj of the Lexico website
                soup = BeautifulSoup(lexico, 'lxml')
                # Find the sections of the page
                for section in soup.find_all('section', class_='gramb'):
                    typ = section.find('span', class_='pos').text
                    d[word]['English'][typ] = list()
                    # Iterate through class 'ind'
                    for cls_ind in section.find_all('span', class_='ind'):
                        # Append English meanings to dictionary
                        d[word]['English'][typ].append(str(cls_ind.text))
                # Read TurEng website
                tureng = requests.get(URL_TUR + word).text
                # Create BeautifulSoup obj of the TurEng website
                soup = BeautifulSoup(tureng, 'lxml')
                # Find the table of the page
                table = soup.find('table')
                # Iterate through class 'tr ts'
                for cls_ind in table.find_all('td', class_='tr ts'):
                    # Append English meanings to dictionary
                    d[word]['Turkish'].append(str(cls_ind.text))
            except Exception as e:
                print(f'Couldnt handle {word}')
                print(f'error: {e}')

# If -learn arg is received
elif sys.argv[1] == '-learn':
    # Declare the prob distribution
    words, prob_dist = calc_prob_dist(d)
    # Get a sample according to the given arg
    for word in random.choice(words, size=int(sys.argv[2]),
                              replace=False, p=prob_dist):
        # Wait for enter to show the meanings
        inp = input(f'{word.upper()}')
        # If it is enter
        if inp == '':
            # Increment times_shown feature by one
            d[word]['times_shown'] += 1
            # Display English meanings
            # Print in a format
            print('English:')
            # Declare English keys
            eng_keys = d[word]['English'].keys()
            # Iterate through keys
            for eng_key in eng_keys:
                print(f'\t{eng_key}:')
                # Iterate through meanings
                for idx, eng_meaning in enumerate(d[word]['English'][eng_key]):
                    # Print English meanings
                    print(f'\t\t{idx}. {eng_meaning}')
            # Display Turkish meanings
            # Print in a format
            print('Turkish:')
            for idx, tur_meaning in enumerate(d[word]['Turkish']):
                # Print Turkish meanings
                print(f'\t{idx}. {tur_meaning}')

    # Write JSON file
writeJSON(d, 'dict')
