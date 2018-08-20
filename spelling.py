from __future__ import division
from collections import Counter, defaultdict
import glob
import re

def tokenize_into_sentences(text):
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    return sentences

def deleted_interpolation(models, curr_spelling, n_grams):
    probablity = 1
    for i in range(len(curr_spelling)-n_grams+1):
        gram = curr_spelling[i:i+n_grams]
        current_words = gram[:-1]
        next_word = gram[-1]
        if not current_words:
            current_words = next_word

        curr_probab = 0
        # multiple language_models
        lambda_param = [1, 0, 0] # assuming trigram model
        for model_number, lambda_of_model in zip(range(len(models)), lambda_param):
            if models[model_number][0].get(current_words, None):
                # divide by total number of words having that count
                next_word_count = models[model_number][0][current_words].get(next_word, 0)
                curr_probab += lambda_of_model * models[model_number][1][next_word_count]
            else:
                # if ngram not found in vocab then assign it probab of unkown
                curr_probab += lambda_of_model * models[model_number][1][0]

            current_words = current_words[1:]
            if not current_words:
                current_words = next_word
            model_number += 1

        probablity *= curr_probab
    return probablity


def good_turing_smoothing(language_model, n_grams, vocab_size):
    print("computing probablities")
    cnc = {}
    for key in language_model.keys():
        for next_word in language_model[key].keys():
            cnc[language_model[key][next_word]] =  cnc.get(language_model[key][next_word], 0) + 1

    total_seen = sum([cnc[key]*key for key in cnc.keys()])
    cnc[0] = pow(vocab_size, n_grams) - total_seen

    cstar = {}
    cnc_keys = sorted(cnc.keys())
    for i in range(len(cnc_keys[:-1])):
        cstar[cnc_keys[i]] = (cnc_keys[i+1] * cnc[cnc_keys[i+1]]) / float(cnc[cnc_keys[i]])

    pstar = {}
    # pstar  here is the total probablity mass assigned to all the grams having same count
    for i in range(len(cnc_keys[:-1])):
        pstar[cnc_keys[i]] = (cstar[cnc_keys[i]] * cnc[cnc_keys[i]]) / float(total_seen)

    # probablity for highest count item
    pstar[cnc_keys[-1]] = cnc[cnc_keys[-1]] / float(total_seen)

    # calculate probablity of one the grams having the count as key
    for key in cnc_keys:
        pstar[key] = pstar[key] / float(cnc[key])

    #import pdb; pdb.set_trace()
    return pstar

def create_character_model(words_freq, n_grams):
    character_model = defaultdict(defaultdict)
    for word in words_freq.keys():
        for i in range(len(word)-n_grams+1):
            sliced = word[i:i+n_grams]
            gram = sliced[:-1]
            next_char = sliced[-1]
            if gram in character_model:
                character_model[gram][next_char] = character_model[gram].get(next_char, 0) + words_freq[word]
            else:
                character_model[gram][next_char] = words_freq[word]

    vocab_size = len(words_freq.keys())

    return character_model, good_turing_smoothing(character_model, n_grams, vocab_size)


def spellcheck(language_models, word_to_check, n_grams):
    # generate candidates
    candidates = [word_to_check]

    return deleted_interpolation(language_models, word_to_check, n_grams)

def main_spelling():
    gutenberg_corpus = glob.glob('./Gutenberg/txt/B*')
    print(len(gutenberg_corpus))
    words_freq = {}

    print("Tokenizing corpus")
    for book in gutenberg_corpus:
        fp = open(book, "r")
        contents = fp.read()
        sentences = tokenize_into_sentences(contents)
        for sentence in sentences:
            tokens = re.split(r'(\b[^\s]+\b)((?<=\.\w).)?', sentence)
            i = 1
            while i < len(tokens):
                if tokens[i].strip().lower().isalpha():
                    curr_tok = '*' + tokens[i].strip().lower() + '$'
                words_freq[curr_tok] = words_freq.get(curr_tok, 0) + 1
                i += 3

    n_grams = 3
    models = []

    for n in range(n_grams+1)[:0:-1]:
        models.append(create_character_model(words_freq, n))

    wrong_spellings = ["intelligemt", "intelligent", "apparantly", "apprently", "calender", "definately", "dilemna", "prononciation", "schepule", "privilede", "occasionelly", "occasionalli", "occasiomally", "occassonally", "occasionatly", "occassionally"]

    for wrong_spelling in wrong_spellings:
        print(wrong_spelling, spellcheck(models, '*'+wrong_spelling+'$', n_grams))
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    # change terms to lowercase or stem them
    main_spelling()
