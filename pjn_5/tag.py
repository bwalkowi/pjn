import os
import json
import requests
import argparse

import regex as re


YEAR = '2008'
INPUT_DIR = '/var/judgments/'
OUTPUT_DIR = 'judgments/'


parser = argparse.ArgumentParser()
parser.add_argument('ip', help='elasticsearch ip')
parser.add_argument('port', help='elasticsearch port')
args = parser.parse_args()
url = f'http://{args.ip}:{args.port}'

files = (os.path.join(INPUT_DIR, file)
         for file in os.listdir(INPUT_DIR)
         if file.startswith('judgments'))

for file in files:
    with open(file) as f:
        judgments = json.load(f)
        for judgment in judgments['items']:
            if judgment['judgmentDate'].startswith(YEAR):
                data = re.sub(r'<[^>]*>|-\n', '', judgment['textContent'],
                              flags=re.WORD)
                ret = requests.post(url, data=data.encode('utf-8'))
                file_name, _ = os.path.splitext(os.path.basename(file))
                output_file = os.path.join(OUTPUT_DIR, f'{file_name}-{judgment["id"]}')
                with open(output_file, mode='wb') as f2:
                    f2.write(ret.content)
