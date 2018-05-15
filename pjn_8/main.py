import os
import pickle
from pprint import pprint
import xml.etree.ElementTree
from collections import Counter

import matplotlib.pyplot as plt


INPUT_DIR = './judgments'
PICKLE_FILE = './categories.pickle'


def read_xmls():
    categories = {}

    for file in os.listdir(INPUT_DIR):
        with open(os.path.join(INPUT_DIR, file)) as f:
            text_xml = xml.etree.ElementTree.fromstring(f.read())

        for item in text_xml.iter():
            if item.tag == 'tok':
                content = ''
                for child in item.getchildren():
                    if child.tag == 'orth':
                        content = child.text
                    if child.tag == 'ann' and int(child.text) >= 1:
                        minor_category = child.attrib['chan']
                        major_category = "_".join(minor_category.split('_')[:2])

                        minor_categories = categories.get(major_category, {})
                        minor_category_counter = minor_categories.get(minor_category, Counter())
                        minor_category_counter.update([content])

                        minor_categories[minor_category] = minor_category_counter
                        categories[major_category] = minor_categories

    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(categories, f)

    return categories


def numbers():
    num = 0
    while True:
        yield num
        num += 1


def histograms(categories, merge_minor=False):
    ids = numbers()
    y_pos = []
    labels = []
    data = []
    for major_cat, minor_categories in categories.items():
        if merge_minor:
            y_pos.append(next(ids))
            labels.append(major_cat)
            quantity = 0
            for minor_counts in minor_categories.values():
                quantity += sum(minor_counts.values())
            data.append(quantity)
        else:
            for minor_cat, counts in minor_categories.items():
                y_pos.append(next(ids))
                labels.append(minor_cat)
                data.append(sum(counts.values()))

    for label, val in zip(labels, data):
        print(f'{label}: {val}')

    plt.bar(y_pos, data, align='center', alpha=0.5)
    if not merge_minor:
        plt.xticks(y_pos, labels, rotation='vertical')
    else:
        plt.xticks(y_pos, labels)
    plt.xlabel('Categories names')
    plt.ylabel('Quantity of each category')
    plt.title(f'{"Major" if merge_minor else "Minor"} categories')
    plt.tight_layout()
    plt.show()


def top_100(categories):
    top = []
    for minor_categories in categories.values():
        for minot_cat, minor_counts in minor_categories.items():
            top.extend([(content, minot_cat, count)
                        for content, count in minor_counts.most_common(100)])
    top.sort(key=lambda x: x[2], reverse=True)
    pprint(top[:100])


def main():
    if os.path.isfile(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            categories = pickle.load(f)
    else:
        categories = read_xmls()

    # histograms(categories)
    # histograms(categories, merge_minor=True)
    top_100(categories)


if __name__ == '__main__':
    main()
