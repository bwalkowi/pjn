import os
import json
import pickle
import argparse
import operator
from math import log2, log
from pprint import pprint
from collections import Counter, defaultdict

import regex as re


YEAR = '2008'
UNIGRAM_STATS_FILE = './unigram_stats.pickle'
BIGRAM_STATS_FILE = './bigram_stats.pickle'
RE_WORD = re.compile(r'\b\p{L}+?\b', re.IGNORECASE)


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


def calc_bigrams_llr_v2(unigram_stats, bigram_stats):
    bigrams_sum = sum(bigram_stats.values())

    def calc_llr(bigram):
        a_b = bigram_stats[bigram]
        a_not_b = unigram_stats[bigram[0]] - a_b
        not_a_b = unigram_stats[bigram[1]] - a_b
        not_a_not_b = bigrams_sum - a_b - a_not_b - not_a_b
        return llr(a_b, a_not_b, not_a_b, not_a_not_b)

    bigrams_llr = [(bigram, calc_llr(bigram)) for bigram in bigram_stats]
    return sorted(bigrams_llr, key=operator.itemgetter(1), reverse=True)


def calc_bigrams_pmi(bigram_stats, unigram_stats):
    bigrams_sum = sum(bigram_stats.values())
    unigram_sum = sum(unigram_stats.values())

    def pmi(bigram):
        fst_prob = unigram_stats[bigram[0]]/unigram_sum
        snd_prob = unigram_stats[bigram[1]]/unigram_sum
        bigram_prob = bigram_stats[bigram]/bigrams_sum
        return log2(bigram_prob/(fst_prob*snd_prob))

    bigrams_pmi = [(bigram, pmi(bigram)) for bigram in bigram_stats]
    return sorted(bigrams_pmi, key=operator.itemgetter(1), reverse=True)


def get_bigrams_from_file(file_path):
    with open(file_path) as file:
        judgments = json.load(file)
        for item in judgments['items']:
            if item['judgmentDate'].startswith(YEAR):
                text = re.sub(r'(-\p{L}\b|<[^>]*>|-\n|\bx+\b)', '',
                              item['textContent'], flags=re.WORD).lower()
                iterator = RE_WORD.finditer(text)
                fst_word = next(iterator).group()
                for match in iterator:
                    word = match.group()
                    yield (fst_word, word)
                    fst_word = word


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


def get_unigram_stats(path):
    with open(path, 'rb') as file:
        return pickle.load(file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir_path',
                        help='path to directory containing judgments')
    args = parser.parse_args()

    unigram_stats = get_unigram_stats(UNIGRAM_STATS_FILE)
    bigram_stats = get_bigram_stats(args.dir_path or BIGRAM_STATS_FILE)

    bigrams_pmi = calc_bigrams_pmi(bigram_stats, unigram_stats)
    print('\nBIGRAMS PMI:')
    pprint(bigrams_pmi[:30])

    bigrams_llr = calc_bigrams_llr(bigram_stats)
    print('\nBIGRAMS LLR:')
    pprint(bigrams_llr[:30])

    bigrams_llr2 = calc_bigrams_llr_v2(unigram_stats, bigram_stats)
    print('\nBIGRAMS LLR2:')
    pprint(bigrams_llr2[:30])


if __name__ == '__main__':
    main()
