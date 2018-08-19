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
        correct_char = max(language_models[0][given_chars], key=language_models[0][given_chars].get)
        given_chars = given_chars[1:]
        model_number += 1

    return word_to_check[:mini[2]] + correct_char + word_to_check[mini[2]+1:]

def create_language_model(words, n_grams):
    language_model = defaultdict(list)
    print("creating inverted index")
    for i in range(len(words)-n_grams+1):
        sliced = words[i:i+n_grams]
        gram = " ".join(sliced[:-1])
        next_word = sliced[-1]
        if not gram:
            gram = next_word
        if gram in language_model:
            language_model[gram].append(next_word)
        else:
            language_model[gram] = [next_word]

    print("computing probablities")
    for key in language_model.keys():
        next_words = language_model[key]
        unique_words = set(next_words)
        nb_words = len(next_words)
        probabilities_given_key = {}
        for unique_word in unique_words:
            probabilities_given_key[unique_word] = \
                float(next_words.count(unique_word)) / nb_words
        language_model[key] = probabilities_given_key
    return language_model

def language_model_for_grammar_detection(n_grams):
    gutenberg_corpus = glob.glob('./Gutenberg/txt/F*')
    words = []

    print("Tokenizing corpus")
    for book in gutenberg_corpus:
        fp = open(book, "r")
        contents = fp.read()
        words += map(lambda x: x.strip().lower(), filter(lambda x: x is not None and x.isalpha() and len(x)!=0,
                re.split(r'(\b[^\s]+\b)((?<=\.\w).)?', contents)))

    models = []
    print("Creating language models")
    for n in range(n_grams+1)[:0:-1]:
        print("create model", n)
        models.append(create_language_model(words, n))
        print("model created")

    return models

def rate_grammar(models, sentence, n_grams):
    probablity = 1

    for i in range(len(sentence)-n_grams+1):
        gram = sentence[i:i+n_grams]
        current_words = " ".join(gram[:-1])
        next_word = gram[-1]
        if not current_words:
            current_words = next_word
        curr_probab = 0
        # multiple language_models
        model_number = 0
        while curr_probab == 0:
            current_words = " ".join(current_words.split(" ")[1:])
            if not current_words:
                current_words = next_word
            if models[model_number].get(current_words, None):
                curr_probab = models[model_number][current_words].get(next_word, 0)
            model_number += 1
        probablity *= curr_probab

    return probablity

def main_grammar():
    n_grams = 3
    models = language_model_for_grammar_detection(n_grams)
    sentences = [["he","is","the","king","of","this","place"], ["he","is","the","king","of","these","place"]]
    for sentence in sentences:
        print(sentence, rate_grammar(models, sentence, n_grams))
    import pdb; pdb.set_trace()

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
    n_grams = 4
    models = []

    for n in range(n_grams+1)[:0:-1]:
        models.append(create_character_model(word_frequency.keys(), n))

    wrong_spellings = ["intelligemt", "apparantly", "calender", "definately", "dilemna", "prononciation", "schepule", "privilede", "occasionelly", "occasionalli", "occasiomally", "occassonally", "occasionatly"]
    for wrong_spelling in wrong_spellings:
        print(wrong_spelling, spellcheck(models, wrong_spelling, n_grams))
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    # change terms to lowercase or stem them
    #main_spelling()
    main_grammar()
