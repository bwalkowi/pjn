import os
import json
import time
from datetime import datetime

import requests
import regex as re


IN_DIR = '../data'
OUT_DIR = './judgments'
JUDGMENTS_TO_PROCESS = 100

USER = 'pjn@student.agh.edu.pl'
TASK = 'any2txt|wcrft2|liner2({"model":"n82"})'
URL = 'http://ws.clarin-pl.eu/nlprest2/base'


def process(data):
    file_id = requests.post(f'{URL}/upload/', data=data.encode('utf-8'),
                            headers={
                                'Content-Type': 'binary/octet-stream'
                            }).text
    task_id = requests.post(url=f'{URL}/startTask/',
                            json={
                                'lpmn': TASK, 'file': file_id, 'user': USER
                            },
                            headers={
                                'Content-Type': 'application/json'
                            }).text

    status = requests.get(url=f'{URL}/getStatus/{task_id}').json()
    while status['status'] in ('QUEUE', 'PROCESSING'):
        time.sleep(0.5)
        status = requests.get(url=f'{URL}/getStatus/{task_id}').json()

    if status['status'] == 'DONE' and status['value']:
        processed_file_id = status['value'][0]['fileID']
        return requests.get(url=f'{URL}/download{processed_file_id}').text

    elif status['status'] == 'ERROR':
        print('Error: ', status['value'])


def process_files(in_dir, out_dir, to_process=100):
    already_processed = 0
    print('\nSTARTING PROCESSING\n\n'
          f'\r[', ' ' * 100, f'] 0% ({already_processed}/{to_process})',
          end='', flush=True)

    files = (file for file in os.listdir(in_dir)
             if re.match(r'judgments-\d+\.json', file))

    for file in sorted(files, key=lambda x: int(x[10:-5])):
        with open(os.path.join(in_dir, file)) as f:
            judgments = json.load(f)

        for judgment in sorted(judgments['items'],
                               key=lambda x: datetime.strptime(x['judgmentDate'], "%Y-%m-%d")):
            if not judgment['judgmentDate'].startswith('2008'):
                continue

            if already_processed == to_process:
                break

            content = process(re.sub(r'<[^>]*>|-\n', '',
                                     judgment['textContent'],
                                     flags=re.WORD))
            if content:
                already_processed += 1
                progress = int((already_processed / to_process) * 100)
                print('\r[', '#' * progress, ' ' * (100 - progress),
                      f'] {progress}% ({already_processed}/{to_process})',
                      end='', flush=True)

                judgment_id = judgment['id']
                out_file = os.path.join(out_dir, f'{file[:-5]}.{judgment_id}')
                with open(out_file, "w") as out_f:
                    out_f.write(content)

    if already_processed < to_process:
        print('\n\nRUN OUT OF JUDGMENTS TO PROCESS\n')
    else:
        print('\n\nFINISHED PROCESSING\n')


if __name__ == '__main__':
    process_files(IN_DIR, OUT_DIR, JUDGMENTS_TO_PROCESS)
