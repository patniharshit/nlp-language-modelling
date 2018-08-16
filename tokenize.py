from __future__ import division
from collections import Counter
import glob
import re

punctuations = re.compile(r"([@#$%^&*()+={}\[\]|:;\"'<>~`'])")

def tokenize():
    pass

def concat_delimiters(delimited_sentences):
    sentences = []
    for element in delimited_sentences:
        if element:
            if element.strip() not in ['.', '?', '!']:
                sentences.append(element.strip())
            else:
                if sentences[-1]:
                    if sentences[-1][-1] in ['.', '?', '!']:
                        sentences[-1] = sentences[-1] + element
                    else:
                        sentences[-1] = sentences[-1] + " " + element
    return sentences

def tokenize_into_sentences(text):
    text = re.sub(r"[\r\n]", r" ", text)
    sentences = concat_delimiters(re.split(r"([\.\?!])", text))
    return sentences

def split_sentence(sentence):
    return re.sub(punctuations, r" \1 ", sentence.strip()).split(" ")

def tokenize_into_words(sentences):
    words = {}
    for sentence in sentences:
        tokens = split_sentence(sentence)
        for token in tokens:
            if token:
                if token in words:
                    words[token] += 1
                else:
                    words[token] = 1
    return words

def spellcheck():
    pass

def main():
    gutenberg_corpus = glob.glob('./Gutenberg/txt/*')
    word_frequency = Counter({})
    sentences = []

    for book in gutenberg_corpus:
        fp = open(book, "r")
        contents = fp.read()

        sentence_arr = tokenize_into_sentences(contents)
        sentences += sentence_arr
        word_dict = tokenize_into_words(sentence_arr)
        word_frequency = word_frequency + Counter(word_dict)

        # remove inverted commas in sentences of the form "[a-z]+\."
        #contents = re.sub(r"\"", r"", contents)
        #assert (len(re.findall(r"\".*\.\"", contents)) == 0)

if __name__ == '__main__':
    # change terms to lowercase or stem them
    main()
