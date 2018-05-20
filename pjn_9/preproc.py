import os
import json

import regex as re


INPUT_DIR = '/var/judgments/'
OUTPUT_DIR = './data/'
SOFT_LIMIT = 1147483648


gathered = 0
files = (file for file in os.listdir(INPUT_DIR)
         if re.match(r'judgments-\d+.json', file))

for file in files:
    with open(os.path.join(INPUT_DIR, file)) as f:
        judgments = json.load(f)

    file_name, file_ext = os.path.splitext(file)
    for judgment in judgments['items']:
        content = re.sub(r'<[^>]*>|-?\n', '', judgment['textContent'],
                         flags=re.WORD)

        with open(os.path.join(OUTPUT_DIR, f'{file_name}.{judgment["id"]}.txt'), 'w') as f2:
            f2.write(content)

        gathered += len(content)

    if gathered >= SOFT_LIMIT:
        break
