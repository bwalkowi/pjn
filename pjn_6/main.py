import os
import random
import argparse
from itertools import groupby

from sklearn.feature_extraction.text import TfidfVectorizer

import regex as re


INPUT_DIR = './judgments/'
RE_WORD = re.compile(r'^[\p{L}\s]+$')
TOP_20 = ['na', 'do', 'art', 'nie', 'że', 'przez', 'ust',
          'się', 'dnia', 'jest', 'oraz', 'ustawy', 'od',
          'sąd', 'nr', 'postępowania', 'pkt', 'tym', 'za',
          'sądu']
TRAIN_RATION = 0.75


def read_document(file_path, normalized):
    with open(file_path) as f:
        if normalized:
            words = (line.rsplit(maxsplit=2)[0].strip()
                     for line in f if line.startswith('\t'))
        else:
            words = (line.split()[0] for line in f if
                     not line.startswith('\t') and len(line) > 1)
        return ' '.join(word for word in words
                        if RE_WORD.match(word) and word not in TOP_20)


def get_documents(normalized=False):
    return {cat: [read_document(os.path.join(INPUT_DIR, file), normalized)
                  for file in files]
            for cat, files in groupby(sorted(os.listdir(INPUT_DIR)),
                                      key=lambda x: x.split('.')[0])}


def prepare_data(documents):
    training_x = []
    training_y = []
    test_x = []
    test_y = []
    for key, values in documents.items():
        docs = list(values)
        labels = [key]*len(docs)
        random.shuffle(docs)
        split_index = int(TRAIN_RATION * len(docs))
        training_x.extend(docs[:split_index])
        training_y.extend(labels[:split_index])
        test_x.extend(docs[split_index:])
        test_y.extend(labels[split_index:])
    return (training_x, training_y), (test_x, test_y)


def prepare_tfidf(training_data, test_data):
    vectorizer = TfidfVectorizer()
    bow_training = vectorizer.fit_transform(training_data)
    bow_test = vectorizer.transform(test_data)
    return bow_training, bow_test


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--normalized', action='store_true')
    args = parser.parse_args()

    training_set, test_set = prepare_data(get_documents(args.normalized))
    training_x, training_y = training_set
    test_x, test_y = test_set
    bow_training_x, bow_test_x = prepare_tfidf(training_x, test_x)
    # print(training_x[0], len(training_x), len(test_y), bow_training_x.shape, bow_test_x.shape, args.normalized)


if __name__ == '__main__':
    main()
