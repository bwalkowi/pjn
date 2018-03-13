import os
import json
import requests
import argparse


def load_data(files_path, url, year):
    count = 0
    for file_path in files_path:
        with open(file_path) as file:
            judgments = json.load(file)
            for judgment in judgments['items']:
                date = judgment['judgmentDate']
                if date.startswith(year):
                    count += 1
                    data = {
                        "content": judgment['textContent'],
                        "date": date,
                        "signature": judgment['id'],
                        "judges": [judge['name'] for judge in judgment['judges']]
                    }
                    ret = requests.post(url, json=data)
                    assert 200 <= ret.status_code <= 300
    print(count)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir_path',
                        default='./json',
                        help='path to directory containing judgments')
    parser.add_argument('-p', '--prefix',
                        default='judgments',
                        help='filename prefix of files with judgments')
    parser.add_argument('-y', '--year', default='2008', help='judgment date')
    parser.add_argument('-i', '--index', default='judgments', help='judgment date')
    parser.add_argument('ip', help='elasticsearch ip')
    parser.add_argument('port', help='elasticsearch port')
    args = parser.parse_args()

    dir_path = args.dir_path
    if os.path.isdir(dir_path):
        files = (os.path.join(dir_path, file)
                 for file in os.listdir(dir_path)
                 if file.startswith(args.prefix))
        load_data(files, f'http://{args.ip}:{args.port}/{args.index}/_doc/',
                  args.year)
    else:
        print(f'Given path ({dir_path}) does not point to directory.')


if __name__ == '__main__':
    main()
