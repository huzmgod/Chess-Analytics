import os
import time
import requests
import re
import json
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser(description='Retrieve chess.com ratings for specified users.')
parser.add_argument('names', metavar='N', type=str, nargs='+',
                    help='a list of usernames to retrieve ratings for')

args = parser.parse_args()

names = {}
for name in args.names:
    names[name] = name

rating = {name: 0 for name in names}

while True:
    for name in names:
        url = f"https://www.chess.com/stats/live/blitz/{name}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(
            'script', string=re.compile('window.chesscom.stats'))
        cadena = script.string
        cadena = cadena.replace('<script>', '').replace('</script>', '')
        match = re.search(r'userData: \{(.*)\}', cadena)
        user_data = "{" + match.group(1) + "}"
        user_data = json.loads(user_data)
        rating[name] = user_data['rating']
    os.system('cls')
    for name in names:
        print(f"{name}: {rating[name]}")
    time.sleep(60)
