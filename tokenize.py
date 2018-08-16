from __future__ import division
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

def main():
    gutenberg_corpus = glob.glob('./Gutenberg/txt/*')
    for book in gutenberg_corpus:
        fp = open(book, "r")
        contents = fp.read()

        sentences = tokenize_into_sentences(contents)
        word_dict = tokenize_into_words(sentences)

        # remove inverted commas in sentences of the form "[a-z]+\."
        #contents = re.sub(r"\"", r"", contents)
        #assert (len(re.findall(r"\".*\.\"", contents)) == 0)

        import pdb; pdb.set_trace()
        break

if __name__ == '__main__':
    main()
