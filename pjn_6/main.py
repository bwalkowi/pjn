import os
import random
import argparse
from itertools import groupby

from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (classification_report,
                             precision_recall_fscore_support)

import regex as re


INPUT_DIR = './judgments/'
RE_WORD = re.compile(r'^[\p{L}\s]+$')
TRAIN_RATIO = 0.75
TOP_20 = ['na', 'do', 'art', 'nie', 'że', 'przez', 'ust',
          'się', 'dnia', 'jest', 'oraz', 'ustawy', 'od',
          'sąd', 'nr', 'postępowania', 'pkt', 'tym', 'za',
          'sądu']


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


def prepare_data(normalized):
    training_x = []
    training_y = []
    test_x = []
    test_y = []
    for category, files in groupby(sorted(os.listdir(INPUT_DIR)),
                                   key=lambda x: x.split('.')[0]):
        judgments = [read_document(os.path.join(INPUT_DIR, file), normalized)
                     for file in files]
        labels = [category] * len(judgments)
        random.shuffle(judgments)

        partition_idx = int(TRAIN_RATIO * len(judgments))
        training_x.extend(judgments[:partition_idx])
        training_y.extend(labels[:partition_idx])
        test_x.extend(judgments[partition_idx:])
        test_y.extend(labels[partition_idx:])

    return training_x, training_y, test_x, test_y


def classify(normalized):
    training_x, training_y, test_x, test_y = prepare_data(normalized)

    vectorizer = TfidfVectorizer()
    bow_training_x = vectorizer.fit_transform(training_x)
    bow_test_x = vectorizer.transform(test_x)

    model = SVC(C=100, kernel='rbf', gamma=0.01)
    model.fit(bow_training_x, training_y)

    prediction = model.predict(bow_test_x)
    micro_avg = precision_recall_fscore_support(test_y, prediction,
                                                average='weighted')[:-1]
    macro_avg = precision_recall_fscore_support(test_y, prediction,
                                                average='macro')[:-1]

    print(classification_report(test_y, prediction),
          f'\nMicro-average: {micro_avg}',
          f'\nMacro-average: {macro_avg}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--normalized', action='store_true')
    args = parser.parse_args()

    classify(args.normalized)


if __name__ == '__main__':
    main()
