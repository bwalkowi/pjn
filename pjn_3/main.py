import os
import json
import pickle
import argparse
from random import sample
from itertools import chain
from collections import Counter

import regex as re
import matplotlib.pyplot as plt


YEAR = '2008'
UNIGRAM_STATS_FILE = './unigram_stats.pickle'
RE_WORD = re.compile(r'\b\p{L}{2,}?\b', re.IGNORECASE)


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
    plt.loglog(list(range(len(frequencies))), frequencies)
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of all most found words')
    plt.show()


def get_words_from_file(file_path):
    with open(file_path) as file:
        judgments = json.load(file)
        for item in judgments['items']:
            if item['judgmentDate'].startswith(YEAR):
                text = re.sub(r'(<[^>]*>|-\n|\bx+\b)', '',
                              item['textContent'], flags=re.WORD).lower()
                for match in RE_WORD.finditer(text):
                    yield match.group()


def get_words_from_files(dir_path):
    files = (os.path.join(dir_path, file_name)
             for file_name in os.listdir(dir_path)
             if file_name.startswith('judgments'))
    for file in files:
        yield from get_words_from_file(file)


def get_unigram_stats(path):
    if os.path.isdir(path):
        unigram_stats = Counter(get_words_from_files(path))
        with open(UNIGRAM_STATS_FILE, 'wb') as file:
            pickle.dump(unigram_stats, file)
    elif os.path.isfile(path):
        with open(path, 'rb') as file:
            unigram_stats = pickle.load(file)
    else:
        raise RuntimeError(f'Specified path ({path}) points to neither '
                           f'valid file nor directory')
    return unigram_stats


def get_known_words(path):
    with open(path) as file:
        return set(line.split(';')[1].lower() for line in file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--polimorfologik',
                        default='./polimorfologik-2.1.txt',
                        help='path to polimorfologik file')
    parser.add_argument('-d', '--dir_path',
                        help='path to directory containing judgments')
    args = parser.parse_args()

    known_words = get_known_words(args.polimorfologik)
    unigram_stats = get_unigram_stats(args.dir_path or UNIGRAM_STATS_FILE)
    unrecognized_words = unigram_stats.keys() - known_words

    draw_histogram(unigram_stats)
    print(len(unigram_stats.keys()), len(unrecognized_words))
    # print(unrecognized_words)

    correct_words(sample(unrecognized_words, 30), known_words, unigram_stats)


if __name__ == '__main__':
    main()
