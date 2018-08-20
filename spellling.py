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

def create_character_model(words_freq, n_grams):
    character_model = defaultdict(list)
    for word in words_freq.keys():
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
        unique_chars = set(next_chars)
        nb_chars = len(next_chars)
        probabilities_given_key = {}
        for unique_char in unique_chars:
            probabilities_given_key[unique_char] = \
                float(next_chars.count(unique_char)) / nb_chars
        character_model[key] = probabilities_given_key
    return character_model

def spellcheck(language_models, word_to_check, n_grams):
    word_to_check = '*' + word_to_check
    mini = (1, "", -1)
    probab_unkown = 0.0001

    for i in range(len(word_to_check)-n_grams+1):
        sliced = word_to_check[i:i+n_grams]
        current = sliced[:-1]
        next_char = sliced[-1]

        probab_given_current = language_models[0][current]
        if probab_given_current:
            probab_next = probab_given_current.get(next_char, 1/float(len(probab_given_current)))
        else:
            probab_next = probab_unkown

        if probab_next < mini[0]:
            mini = (probab_next, current, i+n_grams-1)

    correct_char = None
    model_number = 0
    given_chars = mini[1]
    while correct_char is None:
        correct_char = max(language_models[model_number][given_chars], key=language_models[model_number][given_chars].get)
        given_chars = given_chars[1:]
        model_number += 1

    return word_to_check[:mini[2]] + correct_char + word_to_check[mini[2]+1:]

def main_spelling():
    gutenberg_corpus = glob.glob('./Gutenberg/txt/A*')
    word_frequency = Counter({})
    sentences = []

    for book in gutenberg_corpus:
        fp = open(book, "r")
        contents = fp.read()

        sentence_arr = tokenize_into_sentences(contents)
        sentences += sentence_arr
        word_dict = tokenize_into_words(sentence_arr)
        word_frequency = word_frequency + Counter(word_dict)
        break

    n_grams = 4
    models = []

    for n in range(n_grams+1)[:0:-1]:
        models.append(create_character_model(word_frequency, n))

    wrong_spellings = ["intelligemt", "apparantly", "calender", "definately", "dilemna", "prononciation", "schepule", "privilede", "occasionelly", "occasionalli", "occasiomally", "occassonally", "occasionatly"]
    for wrong_spelling in wrong_spellings:
        print(wrong_spelling, spellcheck(models, wrong_spelling, n_grams))
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    # change terms to lowercase or stem them
    main_spelling()
