from __future__ import division
from collections import Counter, defaultdict
import glob
import re

def tokenize_into_sentences(text):
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    return sentences


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
        backoff_weight = 1
        while curr_probab == 0:
            if models[model_number][0].get(current_words, None):
                # divide by total number of words having that count
                next_word_count = models[model_number][0][current_words].get(next_word, 0)
                curr_probab = models[model_number][1][next_word_count]
            else:
                curr_probab = models[model_number][1][0]

            older_words = current_words
            current_words = " ".join(current_words.split(" ")[1:])
            if not current_words:
                current_words = next_word

            model_number += 1
            """
            if model_number < len(models):
                try:
                    backoff_weight = (1-sum(models[model_number-1][older_words].values()))/(1-sum(models[model_number][current_words].values()))
                except:
                    import pdb; pdb.set_trace()
            print(backoff_weight)
            """
        print(probablity)
        probablity *= curr_probab
    print("-----------------")
    return probablity



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


def good_turing_smoothing(words, n_grams):
    language_model = defaultdict(defaultdict)
    print("creating inverted index")
    for i in range(len(words)-n_grams+1):
        sliced = words[i:i+n_grams]
        gram = " ".join(sliced[:-1])
        next_word = sliced[-1]
        if not gram:
            gram = next_word
        if gram in language_model:
            language_model[gram][next_word] = language_model[gram].get(next_word, 0) + 1
        else:
            language_model[gram] = { next_word : 1 }

    cnc = {}
    for key in language_model.keys():
        for next_word in language_model[key].keys():
            cnc[language_model[key][next_word]] =  cnc.get(language_model[key][next_word], 0) + 1

    vocab_size = len(set(words))
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
    print("computing probablities")
    return language_model, pstar

def language_model_for_grammar_detection(n_grams):
    gutenberg_corpus = glob.glob('./Gutenberg/txt/A*')
    words = []

    print("Tokenizing corpus")
    for book in gutenberg_corpus:
        fp = open(book, "r")
        contents = fp.read()
        sentences = tokenize_into_sentences(contents)
        for sentence in sentences:
            # make this efficient
            # words += ["*"] + map(lambda x: x.strip().lower(), filter(lambda x: x is not None and x.isalpha() and len(x)!=0,
            #        re.split(r'(\b[^\s]+\b)((?<=\.\w).)?', sentence))) + ["$"]
            tokens = re.split(r'(\b[^\s]+\b)((?<=\.\w).)?', sentence)
            words.append('*')
            i = 1
            while i < len(tokens):
                words.append((tokens[i]).strip().lower())
                i += 3
            words.append('$')

    models = []
    print("Creating language models")
    for n in range(n_grams+1)[:0:-1]:
        print("create model", n)
        models.append(good_turing_smoothing(words, n))
        #models.append(create_language_model(words, n))
        print("model created")
    return models


def main_grammar():
    n_grams = 3
    models = language_model_for_grammar_detection(n_grams)
    sentences = [
            ["he","is","the","king","of","this","place"],
            ["he","is", "of","these","place", "the","king"],
            ["that", "lived",  "in", "halls", "i", "dreamt", "i", "marble"],
            ['i', 'dreamt', 'that', 'i', 'lived', 'in', 'marble', 'halls']
        ]
    for sentence in sentences:
        print(sentence, rate_grammar(models, ["*"]+sentence+["$"], n_grams))
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main_grammar()
