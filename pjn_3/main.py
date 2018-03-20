import os
import json
import argparse
from random import sample
from itertools import chain
from collections import Counter
from multiprocessing import Pool

import regex as re
import matplotlib.pyplot as plt
from requests_html import HTML


YEAR = '2008'
ALL_WORDS_OUTPUT_FILE = 'all_words.json'
RE = re.compile(r'\b\p{L}{2,}?\b', re.IGNORECASE)


def edits1(word):
    letters = 'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż'
    splits = [(word[:i], word[i:]) for i in range(len(word)+1)]
    deletes = (L + R[1:] for L, R in splits if R)
    transposes = (L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1)
    replaces = (L + c + R[1:] for L, R in splits if R for c in letters)
    inserts = (L + c + R for L, R in splits for c in letters)
    return set(chain(deletes, transposes, replaces, inserts))


def edits2(word):
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def filter_known(words, known_words):
    return {word for word in words if word in known_words}


def correct_word(word, known_words, all_words):
    all_words_count = sum(all_words.values())
    candidates = (filter_known([word], known_words)
                  or filter_known(edits1(word), known_words)
                  or filter_known(edits2(word), known_words)
                  or [word])
    return max(candidates, key=lambda w: all_words[w]/all_words_count)


def correct_words(unrecognized_words, known_words, all_words):
    corrected_words = {word: correct_word(word, known_words, all_words)
                       for word in unrecognized_words}
    print(corrected_words)


def draw_histogram(all_words):
    _, frequencies = zip(*all_words.most_common())
    x = list(range(len(frequencies)))

    plt.loglog(x, frequencies)
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of all most found words')
    plt.show()


def get_words_from_file(path):
    words = []
    with open(path) as file:
        judgments = json.load(file)
        for item in judgments['items']:
            if item['judgmentDate'].startswith(YEAR):
                text = re.sub(r'(-\n|\bx+\b)', '', item['textContent'],
                              flags=re.WORD).lower()
                html = HTML(html=text)
                words.extend(RE.findall(html.text))
    return words


def get_all_words(path):
    if os.path.isdir(path):
        files = (os.path.join(path, file_name)
                 for file_name in os.listdir(path)
                 if file_name.startswith('judgments'))
        with Pool(processes=os.cpu_count() or 2) as pool:
            all_words = Counter(chain(*pool.map(get_words_from_file, files)))
        with open(ALL_WORDS_OUTPUT_FILE, 'w') as file:
            json.dump(all_words, file)
    elif os.path.isfile(path):
        with open(path) as file:
            all_words = Counter(json.load(file))
    else:
        raise RuntimeError(f'Specified path ({path}) does not point to '
                           f'valid file or directory')
    return all_words


def get_known_words(path):
    with open(path) as file:
        return set(line.split(';')[1].lower() for line in file)


def main():
    parser = argparse.ArgumentParser()
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

    known_words = get_known_words(args.polimorfologik)
    all_words = get_all_words(args.input or args.dir_path)
    unrecognized_words = all_words.keys() - known_words

    draw_histogram(all_words)
    print(len(all_words.keys()), len(unrecognized_words))
    # print(unrecognized_words)

    correct_words(sample(unrecognized_words, 30), known_words, all_words)


if __name__ == '__main__':
    main()
