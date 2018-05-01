import os
import pickle
import argparse
import operator
from math import log
from pprint import pprint
from collections import Counter, defaultdict


YEAR = '2008'
BIGRAM_STATS_FILE = './bigram_stats.pickle'


def denorm_entropy(*args):
    n = sum(args)
    return -sum(0 if k == 0 else k*log(k/n) for k in args)


def llr(a_b, not_a_b, a_not_b, not_a_not_b):
    matrix_entropy = denorm_entropy(a_b, not_a_b, a_not_b, not_a_not_b)
    rows_entropy = denorm_entropy(a_b + not_a_b, a_not_b + not_a_not_b)
    cols_entropy = denorm_entropy(a_b + a_not_b, not_a_b + not_a_not_b)
    return 2 * (rows_entropy + cols_entropy - matrix_entropy)


def calc_bigrams_llr(bigram_stats):
    bigrams_sum = sum(bigram_stats.values())
    contingency_table = defaultdict(lambda: defaultdict(int))
    rev_contingency_table = defaultdict(lambda: defaultdict(int))
    for (fst, snd) in bigram_stats:
        occurrences = bigram_stats[(fst, snd)]
        contingency_table[fst][snd] += occurrences
        rev_contingency_table[snd][fst] += occurrences

    def calc_llr(bigram):
        a, b = bigram
        a_b = contingency_table[a][b]
        a_not_b = sum(contingency_table[a].values()) - a_b
        not_a_b = sum(rev_contingency_table[b].values()) - a_b
        not_a_not_b = bigrams_sum - a_b - a_not_b - not_a_b
        return llr(a_b, a_not_b, not_a_b, not_a_not_b)

    bigrams_llr = [(bigram, calc_llr(bigram)) for bigram in bigram_stats]
    return sorted(bigrams_llr, key=operator.itemgetter(1), reverse=True)


def get_bigrams_from_file(file_path):
    words = []
    prev_line = ''
    with open(file_path) as file:
        for line in file:
            if line.startswith('\t') and 'interp' not in line:
                word, tag, _ = line.rsplit(maxsplit=2)
                category = tag.split(':')[0]
                if category == 'brev':
                    word = prev_line.split()[0]
                else:
                    word = ' '.join(word.split())
                words.append((word.lower(), category))
            prev_line = line

    following_words = iter(words)
    next(following_words)
    for fst_word, snd_word in zip(words, following_words):
        yield (fst_word, snd_word)


def get_bigrams_from_files(dir_path):
    files = (os.path.join(dir_path, file_name)
             for file_name in os.listdir(dir_path)
             if file_name.startswith('judgments'))
    for file in files:
        yield from get_bigrams_from_file(file)


def get_bigram_stats(path):
    if os.path.isdir(path):
        bigram_stats = Counter(get_bigrams_from_files(path))
        with open(BIGRAM_STATS_FILE, 'wb') as file:
            pickle.dump(bigram_stats, file)
    elif os.path.isfile(path):
        with open(path, 'rb') as file:
            bigram_stats = pickle.load(file)
    else:
        raise RuntimeError(f'Specified path ({path}) points to neither '
                           f'valid file nor directory')
    return bigram_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir_path',
                        help='path to directory containing judgments')
    args = parser.parse_args()

    bigram_stats = get_bigram_stats(args.dir_path or BIGRAM_STATS_FILE)
    bigrams_llr = calc_bigrams_llr(bigram_stats)

    def pred(record):
        (((w1, cat1), (w2, cat2)), _) = record
        return cat1 == 'subst' and (cat2 == 'subst' or cat2.startswith('adj'))

    selected_bigrams = list(filter(pred, bigrams_llr))
    pprint(selected_bigrams[:30])


if __name__ == '__main__':
    main()
