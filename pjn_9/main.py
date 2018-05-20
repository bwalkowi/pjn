from pprint import pprint

from gensim.models import Word2Vec


MODEL = './model'


def sanitize(phrase):
    return phrase.lower().replace(' ', '_')


def ex1(wv):
    phrases = [
        "Sąd Najwyższy",
        "Trybunał Konstytucyjny",
        "kodeks cywilny",
        "kpk",
        "sąd rejonowy",
        "szkoda",
        "wypadek",
        "kolizja",
        "szkoda majątkowa",
        "nieszczęście",
        "rozwód"
    ]

    for phrase in phrases:
        print('\n', phrase)
        pprint(wv.most_similar(sanitize(phrase), topn=3))


def ex2(wv):
    operands = [
        ("Sąd Najwyższy", "kpc", "konstytucja"),
        ("pasażer", "mężczyzna", "kobieta"),
        ("samochód", "droga", "rzeka")
    ]
    for a, b, c in operands:
        result = wv[sanitize(a)] - wv[sanitize(b)] + wv[sanitize(c)]
        print(f'\n{a} - {b} + {c}:')
        pprint(wv.similar_by_vector(result, topn=5))
        # pprint(wv.most_similar(positive=[sanitize(a), sanitize(c)],
        #                        negative=[sanitize(b)], topn=5))
        # pprint(wv.most_similar_cosmul(positive=[sanitize(a), sanitize(c)],
        #                               negative=[sanitize(b)], topn=5))


def ex3(wv):
    phrases = [
        "szkoda",
        "strata",
        "uszczerbek",
        "szkoda majątkowa",
        # "uszczerbek na zdrowiu",
        "krzywda",
        "niesprawiedliwość",
        "nieszczęście"
    ]
    pass


def main():
    model = Word2Vec.load(MODEL)
    wv = model.wv
    # ex1(wv)
    # ex2(wv)
    ex3(wv)


if __name__ == '__main__':
    main()
