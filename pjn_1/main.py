import os
import re
import json
import argparse
from itertools import chain
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool


YEAR = '2008'

THRESHOLD = 10**6

# taken from http://dziennikustaw.gov.pl/du/1964/s/16/93
JOURNAL_NO = 16
JOURNAL_YEAR = 1964
JOURNAL_ENTRY = 93
# JOURNAL_TITLE = 'Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny'

RE_1 = re.compile(r'(((?P<val>\d[\d,.\s]*-?\s*)'       # wartosc

                  # mln/tys/itd, take what you can and enetually throw away at later processing
                  r'(?P<abbrev>[a-ząęśćó]+\.?)??\s*'

                  # zlote
                  r'(pln|(now|star)(y(mi?|ch)?|e(go|mu)?))?\s*'
                  r'(pln|zł(ot(y(mi?|ch)?|e(go|mu)?))?))\s*'

                  # grosze
                  r'((?P<gr>\d{1,2})\s*gr(osz(a(mi|ch)?|em?|y|u|o(m|wi)))?)?\b)|'
                  r'((?P<gr2>\d{1,2})\s*gr(osz(a(mi|ch)?|em?|y|u|o(m|wi)))?)\b',

                  re.IGNORECASE | re.VERBOSE)

RE_3 = re.compile(r'\bart.?\s*445\b', re.IGNORECASE)

RE_4 = re.compile(r'\b(szk(?:ód|od(?:ą|ę|y|om?|zie|a(?:mi|ch)?)))\b',
                  re.IGNORECASE)

ABBREV_2_MULTIPLIER = {
    'tys': 10**3,
    'tyś': 10**3,
    'tysiąca': 10**3,
    'tysięcy': 10**3,
    'mln': 10**6,
    'milion': 10**6,
    'miliona': 10**6,
    'milionów': 10**6,
    'min': 10**6,
    'mld': 10**9,
    'st': 1,
    'znala': None,
    'o': None,
}


def normalize(token):
    match = RE_1.match(token)

    # same grosze
    gr2 = match.group('gr2')
    if gr2:
        return float(gr2)/100

    val = match.group('val').strip().rstrip(',. -')
    abbrev = match.group('abbrev')
    gr = match.group('gr')

    if abbrev:
        val = float(''.join(re.sub(r'[\s,.]*', '', char) for char in val))
        multiplier = ABBREV_2_MULTIPLIER.get(abbrev.strip(' .').lower(), None)
        if not multiplier:
            return None
        else:
            val *= multiplier
    else:
        if len(val) > 2 and val[-2] in (',', '.'):
            a, b = val[:-2], val[-1:]
        elif len(val) > 3 and val[-3] in (',', '.'):
            a, b = val[:-3], val[-2:]
        else:
            a, b = val, '0'

        a = ''.join(re.sub(r'[\s,.]*', '', char) for char in val)
        val = float(a) + float(b)/100

    if gr:
        val += float(gr)/100

    return val


def worker_fun1(path):
    values = []
    with open(path) as file:
        judgments = json.load(file)
        for judgment in judgments['items']:
            if judgment['judgmentDate'].startswith(YEAR):
                for match in RE_1.finditer(judgment['textContent']):
                    val = match.group().replace('\n', '')
                    print(val)
                    # print(os.path.basename(path), judgment['id'], match.group().replace('\n', ''), sep=';')
                    num = normalize(val)
                    if num is not None:
                        values.append(num)
    return values


def reduce_fun1(results):
    l1 = []
    l2 = []
    for num in chain(*results):
        if num <= THRESHOLD:
            l1.append(num)
        else:
            l2.append(num)

    l3 = l1+l2
    print(len(l3))

    bins = np.logspace(0, 16, 100)

    plt.hist(l1, bins=bins)
    plt.gca().set_xscale('log')
    plt.title('Kwoty poniżej 1 mln')
    plt.xlabel('Kwoty [zł]')
    plt.ylabel('Liczba wystąpień')
    plt.show()

    plt.hist(l2, bins=bins)
    plt.gca().set_xscale('log')
    plt.title('Kwoty powyżej 1 mln')
    plt.xlabel('Kwoty [zł]')
    plt.ylabel('Liczba wystąpień')
    plt.show()

    plt.hist(l3, bins=bins)
    plt.gca().set_xscale('log')
    plt.title('Wszystkie kwoty')
    plt.xlabel('Kwoty [zł]')
    plt.ylabel('Liczba wystąpień')
    plt.show()


def worker_fun3(path):
    counter = 0
    with open(path) as file:
        judgments = json.load(file)
        for item in judgments['items']:
            if item['judgmentDate'].startswith(YEAR):
                if any(ref['journalNo'] == JOURNAL_NO
                       and ref['journalYear'] == JOURNAL_YEAR
                       and ref['journalEntry'] == JOURNAL_ENTRY
                       and RE_3.search(ref['text'])
                       for ref in item['referencedRegulations']):
                    counter += 1
                    print(os.path.basename(path), item['id'])
    return counter


def reduce_fun3(results):
    print(f'There is {sum(count for count in results)} such judgments.')


def worker_fun4(path):
    counter = 0
    with open(path) as file:
        judgments = json.load(file)
        for item in judgments['items']:
            if item['judgmentDate'].startswith(YEAR):
                match = RE_4.search(item['textContent'])
                if match:
                    counter += 1
                    print(os.path.basename(path), item['id'], match.group())
    return counter


EX2FUNC = {
    'ex1': (worker_fun1, reduce_fun1),
    'ex3': (worker_fun3, reduce_fun3),
    'ex4': (worker_fun4, reduce_fun3),
}


def main():
    cores = os.cpu_count()
    if not cores:
        cores = 1

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--pool_size',
                        default=cores, type=int,
                        help='processes pool size')
    parser.add_argument('-d', '--dir_path',
                        default='./json',
                        help='path to directory containing judgments')
    parser.add_argument('-p', '--prefix',
                        default='judgments',
                        help='filename prefix of files with judgments')
    parser.add_argument('ex', choices=['ex1', 'ex3', 'ex4'],
                        help='exercise to perform')
    args = parser.parse_args()

    dir_path = args.dir_path
    if os.path.isdir(dir_path):
        pool = Pool(processes=args.pool_size)
        files = (os.path.join(dir_path, file)
                 for file in os.listdir(dir_path)
                 if file.startswith(args.prefix))
        worker_fun, reduce_fun = EX2FUNC[args.ex]
        reduce_fun(pool.imap(worker_fun, files))
    else:
        print(f'Given path ({dir_path}) does not point to directory.')


if __name__ == '__main__':
    main()
