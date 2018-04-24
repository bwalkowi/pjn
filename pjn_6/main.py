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
TOP_20 = [
    'na', 'do', 'art', 'nie', 'że', 'przez', 'ust',
    'się', 'dnia', 'jest', 'oraz', 'ustawy', 'od',
    'sąd', 'nr', 'postępowania', 'pkt', 'tym', 'za',
    'sądu'
]
CATEGORIES = {
    'ac': 'Sprawy cywilne',
    'au': 'Sprawy z zakresu ubezpieczenia społecznego',
    'ak': 'Sprawy karne',
    'g': 'Sprawy gospodarcze',
    'ap': 'Sprawy w zakresie prawa pracy',
    'r': 'Sprawy w zakresie prawa rodzinnego',
    'w': 'Sprawy o wykroczenia',
    'am': 'Sprawy w zakresie prawa konkurencji'
}


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

    micro_true = []
    micro_pred = []
    macro_metrics = [0, 0, 0]
    categories_num = 0

    for abbrev, category in CATEGORIES.items():
        categories_num += 1
        bin_training_y = [0 if label == abbrev else 1 for label in training_y]
        bin_test_y = [0 if label == abbrev else 1 for label in test_y]

        model = SVC(C=100, kernel='rbf', gamma=0.01)
        model.fit(bow_training_x, bin_training_y)

        prediction = model.predict(bow_test_x)

        metrics = precision_recall_fscore_support(bin_test_y, prediction,
                                                  pos_label=0, average='binary')
        precision, recall, f1_score, _ = metrics

        micro_true.extend(bin_test_y)
        micro_pred.extend(prediction)
        macro_metrics[0] += precision
        macro_metrics[1] += recall
        macro_metrics[2] += f1_score

        print(f'{category}:\n\n'
              f'Precision: {precision}\n'
              f'Recall: {recall}\n'
              f'F1 score: {f1_score}\n',
              # classification_report(bin_test_y, prediction),
              '------------------------------------------------------')

    micro_metrics = precision_recall_fscore_support(micro_true, micro_pred,
                                                    pos_label=0, average='binary')
    micro_precision, micro_recall, micro_f1_score, _ = micro_metrics
    macro_precision, macro_recall, macro_f1_score = [x / categories_num
                                                     for x in macro_metrics]

    print('\nMicro-average: ', (micro_precision, micro_recall, micro_f1_score),
          '\nMacro-average: ', (macro_precision, macro_recall, macro_f1_score))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--normalized', action='store_true')
    args = parser.parse_args()

    classify(args.normalized)


if __name__ == '__main__':
    main()
