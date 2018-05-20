import os

from tqdm import tqdm
from nltk import sent_tokenize, TweetTokenizer
from gensim.models import Phrases, Word2Vec
from gensim.models.phrases import Phraser


CORPUS_DIR = './data/'
BIGRAM = './bigram'
TRIGRAM = './trigram'
MODEL = './model'


def corpus(directory):
    word_tokenizer = TweetTokenizer(preserve_case=False)
    for file in tqdm(os.listdir(directory)):
        with open(os.path.join(directory, file)) as f:
            text = f.read()

        for sentence in sent_tokenize(text, language='polish'):
            yield word_tokenizer.tokenize(sentence)


def get_bigram_phraser(directory):
    if os.path.isfile(BIGRAM):
        return Phraser.load(BIGRAM)
    else:
        bigram = Phraser(Phrases(corpus(directory)))
        bigram.save(BIGRAM)
        return bigram


def get_trigram_phraser(directory):
    if os.path.isfile(TRIGRAM):
        return Phraser.load(TRIGRAM)
    else:
        bigram = get_bigram_phraser(directory)
        sentence_stream = (bigram[sentence] for sentence in corpus(directory))
        trigram = Phraser(Phrases(sentence_stream))
        trigram.save(TRIGRAM)
        return trigram


def main():
    bigram = get_bigram_phraser(CORPUS_DIR)
    trigram = get_trigram_phraser(CORPUS_DIR)
    sentences = [trigram[bigram[sentence]] for sentence in corpus(CORPUS_DIR)]
    model = Word2Vec(sentences, window=5, size=300, sg=0,
                     workers=os.cpu_count(), min_count=3)
    model.save(MODEL)


if __name__ == '__main__':
    main()
