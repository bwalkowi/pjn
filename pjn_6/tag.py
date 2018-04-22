import os
import json
import requests
import argparse
from collections import Counter
from typing import Iterable, Dict

import regex as re


START_YEAR = 2008
END_YEAR = 2015
INPUT_DIR = '/var/judgments/'
OUTPUT_DIR = 'judgments/'
COURT_TYPES = ('COMMON', 'SUPREME')
MIN_MEMBERS_NUM = 100
COURT_CASES = {
    'ac': r'\bA?C.*?\b',
    'au': r'\bA?U.*?\b',
    'ak': r'\bA?K.*?\b',
    'g': r'\bG.*?\b',
    'ap': r'\bA?P.*?\b',
    'r': r'\bR.*?\b',
    'w': r'\bW.*?\b',
    'am': r'\bAm.*?\b'
}

RE_JUSTIFICATION = re.compile(r'\n\s*' + r'\s*'.join(c for c in 'uzasadnienie')
                              + r'\s*\n', flags=re.IGNORECASE)


def tag_judgments(url: str, year: int, court_cases: Dict[str, str], *,
                  court_types: Iterable[str] = COURT_TYPES):
    files = (file for file in os.listdir(INPUT_DIR)
             if re.match(r'judgments-\d+\.json', file))

    for file in sorted(files, key=lambda x: int(x[10:-5])):
        with open(os.path.join(INPUT_DIR, file)) as f:
            judgments = json.load(f)

        judgments_year = int(judgments['items'][0]['judgmentDate'][:4])
        if judgments_year < year:
            break
        elif judgments_year > year:
            return

        for judgment in judgments['items']:
            if judgment['courtType'] not in court_types:
                continue

            case_number = judgment['courtCases'][0]['caseNumber']
            for court_case, court_case_re in court_cases.items():
                if re.search(court_case_re, case_number):
                    break
            else:
                continue

            content = re.sub(r'<[^>]*>|-\n', '', judgment['textContent'],
                             flags=re.WORD)
            justification = RE_JUSTIFICATION.search(content)
            if justification:
                data = content[justification.end():]
                ret = requests.post(url, data=data.encode('utf-8'))
                if ret.status_code != 200:
                    continue

                file_id = file[10:-5]
                judgment_id = judgment["id"]
                file2 = f'{court_case}.{year}.{file_id}.{judgment_id}.txt'
                with open(os.path.join(OUTPUT_DIR, file2), mode='wb') as f2:
                    f2.write(ret.content)

                yield court_case


def prepare_judgments(url, start_year=START_YEAR, end_year=END_YEAR):
    court_cases = COURT_CASES
    tagged_court_cases = Counter({court_case: 0
                                  for court_case in court_cases})
    for year in range(start_year, end_year):
        tagged_court_cases.update(Counter(tag_judgments(url, year, court_cases)))
        court_cases = {court_case: court_case_re
                       for court_case, court_case_re in court_cases.items()
                       if tagged_court_cases[court_case] < MIN_MEMBERS_NUM}
        if not court_cases:
            break

    return tagged_court_cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ip', default='localhost',
                        help='krnnt docker ip')
    parser.add_argument('-p', '--port', default='9200',
                        help='krnnt docker port')
    args = parser.parse_args()

    print(prepare_judgments(f'http://{args.ip}:{args.port}'))


if __name__ == '__main__':
    main()
