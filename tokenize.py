from __future__ import division
from collections import Counter, defaultdict
import glob
import re

def tokenize_into_sentences(text):
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    return sentences

def tokenize_into_words(sentences):
    words = {}
    for sentence in sentences:
        tokens = re.split(r'(\b[^\s]+\b)((?<=\.\w).)?', sentence)
        for word in tokens:
            if word and word.isalpha():
                word = word.strip().lower()
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
    return words

def create_character_model(words, n_grams):
    character_model = defaultdict(list)
    for word in words:
        word = '*' + word + '$'
        for i in range(len(word)-n_grams+1):
            sliced = word[i:i+n_grams]
            gram = sliced[:-1]
            next_char = sliced[-1]
            if gram in character_model:
                character_model[gram].append(next_char)
            else:
                character_model[gram] = [next_char]

    for key in character_model.keys():
        next_chars = character_model[key]
        unique_chars = set(next_chars) # removes duplicated
        nb_chars = len(next_chars)
        probabilities_given_key = {}
        for unique_char in unique_chars:
            probabilities_given_key[unique_char] = \
                float(next_chars.count(unique_char)) / nb_chars
        character_model[key] = probabilities_given_key
    import pdb; pdb.set_trace()
    return character_model

def spellcheck(words, word_to_check):
    character_model = create_character_model(words, 3)
    import pdb; pdb.set_trace()
    return character_model

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
        print(spellcheck(word_frequency.keys(), "harshit"))
        # remove inverted commas in sentences of the form "[a-z]+\."
        #contents = re.sub(r"\"", r"", contents)
        #assert (len(re.findall(r"\".*\.\"", contents)) == 0)
        break

if __name__ == '__main__':
    # change terms to lowercase or stem them
    main()
