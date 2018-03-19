import os
import json
import argparse
from fnmatch import fnmatch
from itertools import chain
from collections import Counter
from multiprocessing import Pool

import numpy as np
import matplotlib.pyplot as plt

import regex as re
from requests_html import HTML


YEAR = '2008'
HIST_WORDS_NUM = 30
RE = re.compile(r'\b\p{L}{2,}?\b', re.IGNORECASE)


# def words1(text): return re.findall(r'\w+', text.lower())
#
# WORDS = Counter(words1(open('big.txt').read()))
#
#
# def P(word, N=sum(WORDS.values())):
#     "Probability of `word`."
#     return WORDS[word] / N
#
#
# def correction(word):
#     "Most probable spelling correction for word."
#     return max(candidates(word), key=P)
#
#
# def candidates(word):
#     "Generate possible spelling corrections for word."
#     return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])
#
#
# def known(words):
#     "The subset of `words` that appear in the dictionary of WORDS."
#     return set(w for w in words if w in WORDS)
#
#
# def edits1(word):
#     "All edits that are one edit away from `word`."
#     letters    = 'abcdefghijklmnopqrstuvwxyz'
#     splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
#     deletes    = [L + R[1:]               for L, R in splits if R]
#     transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
#     replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
#     inserts    = [L + c + R               for L, R in splits for c in letters]
#     return set(deletes + transposes + replaces + inserts)
#
#
# def edits2(word):
#     "All edits that are two edits away from `word`."
#     return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def get_words_from_file(path):
    words = []
    with open(path) as file:
        judgments = json.load(file)
        for item in judgments['items']:
            if item['judgmentDate'].startswith(YEAR):
                html = HTML(html=item['textContent'])
                text = re.sub(r'-\n|\bx+\b', '', html.text,
                              flags=re.WORD).lower()
                words.extend(RE.findall(text))
    return words


def get_all_words(path, pool):
    if os.path.isdir(path):
        files = (os.path.join(path, file_name)
                 for file_name in os.listdir(path)
                 if fnmatch(file_name, 'judgments-*.json'))
        all_words = Counter(chain(*pool.map(get_words_from_file, files)))
        with open('./all_words.json', 'w') as file:
            json.dump(all_words, file)
    elif os.path.isfile(path):
        with open(path) as file:
            all_words = Counter(json.load(file))
    else:
        raise RuntimeError(f'Specified path ({path}) does not point to '
                           f'valid file or directory')

    words, frequencies = zip(*all_words.most_common(n=HIST_WORDS_NUM))

    x = np.arange(len(words))
    plt.bar(x, frequencies, align='center', alpha=0.5, log=True)
    plt.xticks(x, words, rotation='vertical')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of {HIST_WORDS_NUM} most common words')
    plt.show()

    return all_words


def get_correct_words(path):
    with open(path) as file:
        return {line.split(';')[1].lower() for line in file}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--pool_size',
                        default=os.cpu_count() or 1,
                        type=int, help='processes pool size')
    parser.add_argument('-p', '--polimorfologik',
                        default='./polimorfologik-2.1.txt',
                        help='path to polimorfologik file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dir_path',
                       default='../data',
                       help='path to directory containing judgments')
    group.add_argument('-i', '--input',
                       help='path to file containing words frequency')
    args = parser.parse_args()

    correct_words = get_correct_words(args.polimorfologik)
    with Pool(processes=args.pool_size) as pool:
        all_words = get_all_words(args.input or args.dir_path, pool)
        unrecognized_words = all_words.keys() - correct_words

        print(len(all_words.keys()), len(unrecognized_words))
        # print(unrecognized_words)


if __name__ == '__main__':
    main()
