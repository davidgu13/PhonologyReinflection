from itertools import chain
from g2p_config import idx2feature, feature2idx, p2f_dict, f2p_dict, langs_properties, general_punctuations
from functools import partial

def joinit(iterable, delimiter):
    # Inserts delimiters between elements of some iterable object.
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x

def tuple_of_phon_tuples2phon_sequence(tupleOfTuples) -> [str]:
    return list(chain(*joinit(tupleOfTuples, ('$',))))


class LanguageSetup:
    """
    Stores the letters and phonemes of the language. Further logic includes converting words to phonemes and vice versa.
    Note: the class is implemented to fit to Georgian, Russian and several Indo-European languages. For languages with more complex phonology,
    this class might need to be extended/be inherited from.
    """
    def __init__(self, lang_name: str, graphemes2phonemes:dict, manual_word2phonemes=None, manual_phonemes2word=None):
        self._name = lang_name
        self._graphemes2phonemes = graphemes2phonemes
        self._graphemes2phonemes.update(dict(zip(general_punctuations, general_punctuations)))
        self._phonemes2graphemes = {v:k for k, v in self._graphemes2phonemes.items()} # _graphemes2phonemes.reverse

        self._alphabet = self._graphemes2phonemes.keys() # the graphemes of the language
        self._phonemes = self._graphemes2phonemes.values()

        self._manual_word2phonemes = manual_word2phonemes
        self._manual_phonemes2word = manual_phonemes2word

    def get_lang_name(self): return self._name
    def get_lang_alphabet(self): return self._alphabet
    def get_lang_phonemes(self): return self._phonemes

    def word2phonemes(self, word:str, mode:str) -> [[int]]:
        """
        Convert a word (sequence of graphemes) to a list of phoneme tuples.
        :param word: word
        :param mode: can be either 'features' or 'phonemes' (see more above).
        :return: ((,,), (,,), (,,), ...) or list(*IPA symbols*)
        """
        assert mode in {'features', 'phonemes'}, f"Mode {mode} is invalid"

        word = word.casefold() # lower-casing
        graphemes = list(word) # beware of Niqqud-like symbols

        if self._manual_word2phonemes:
            phonemes = self._manual_word2phonemes(graphemes)
        else:
            phonemes = [self._graphemes2phonemes[g] for g in graphemes]

        if mode=='phonemes':
            return phonemes
        else: # mode=='features'
            features=[]
            for p in phonemes:
                feats = [str(feature2idx[e]) for e in p2f_dict[p]]
                feats.extend(['NA']*(MAX_FEAT_SIZE-len(feats)))
                if PHON_USE_ATTENTION:
                    feats.append(p)
                features.append(tuple(feats))
            features = tuple_of_phon_tuples2phon_sequence(features)
            return features


    def phonemes2word(self, phonemes: [[int]], mode:str) -> str:
        """
        Convert a list of phoneme tuples to a word (sequence of graphemes)
        :param phonemes: [(,,), (,,), (,,), ...] or (*IPA symbols*)
        :param mode: can be either 'features' or 'phonemes' (see more above).
        :return: word
        """
        assert mode in {'features', 'phonemes'}, f"Mode {mode} is invalid"

        if mode=='phonemes':
            if self._manual_phonemes2word:
                graphemes = self._manual_phonemes2word(phonemes)
            else:
                graphemes = [self._phonemes2graphemes[p] for p in phonemes]
        else: # mode=='features'
            graphemes = []
            for f_tuple in phonemes:
                if PHON_USE_ATTENTION:
                    p = f_tuple[-1]
                    g = self._phonemes2graphemes[p]
                else:
                    f_tuple = tuple(idx2feature[int(i)] for i in f_tuple if i != 'NA')
                    p = f2p_dict.get(f_tuple)

                    if p is None: g = '#'
                    else: g = self._phonemes2graphemes[p]
                graphemes.append(g)
        return ''.join(graphemes)

def twoWay_conversion(w):
    print(f"w = {w}")
    ps = langPhonology.word2phonemes(w, mode='phonemes')
    feats = langPhonology.word2phonemes(w, mode='features')
    print(f"phonemes = {ps}")
    print(f"features = {feats}")
    print(f"p2word: {langPhonology.phonemes2word(ps, mode='phonemes')}")
    feats = [f.split(',') for f in ','.join(feats).split(',$,')]
    w_reconstructed = langPhonology.phonemes2word(feats, mode='features')
    print(f"f2word: {w_reconstructed}")
    print(f"ED(w, f2word) = {editDistance(w, w_reconstructed)}")

# Change this to True only when debugging the g2p/p2g conversions!
debugging_mode = True
if debugging_mode:
    PHON_USE_ATTENTION, lang = True, 'kat'
else:
    from hyper_params_config import PHON_USE_ATTENTION, lang


MAX_FEAT_SIZE = max([len(p2f_dict[p]) for p in langs_properties[lang][0].values()])
langPhonology = LanguageSetup(lang, langs_properties[lang][0], langs_properties[lang][1], langs_properties[lang][2])

# d = dict(zip(alphabet, phonemes))
# phon_d = dict(zip(phonemes, alphabet))
#
# # w = list('найяснюотщööо') # bul
# # w = list('eéfdzgycsklynndzso') # hun
# w = list('bщvnmngodzsnkoxeööj')
# print(f"w = {w}")
# ps = word2phonemes_with_digraphs(w, d, single_phonemes)
# print(f"ph= {ps}")
# w2 = phonemes2graphemes_with_doubles(ps, phon_d)
# print(f"w2= {w2}")
import numpy as np
def editDistance(str1, str2):
    """Simple Levenshtein implementation"""
    table = np.zeros([len(str2) + 1, len(str1) + 1])
    for i in range(1, len(str2) + 1):
        table[i][0] = table[i - 1][0] + 1
    for j in range(1, len(str1) + 1):
        table[0][j] = table[0][j - 1] + 1
    for i in range(1, len(str2) + 1):
        for j in range(1, len(str1) + 1):
            if str1[j - 1] == str2[i - 1]:
                dg = 0
            else:
                dg = 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + dg)
    return int(table[len(str2)][len(str1)])
# print(f"ED = {editDistance(w,w2)



if __name__ == '__main__':
    example_words = {'kat': 'მჭირდებოდნენ', 'swc': 'magongjwa', 'sqi': 'rije rrçlldijdhegnj', 'hun': 'hűdályokról', 'bul': 'най-ясното',
                     'lav': 'abstrahēšana', 'fin': 'ilmaatyynyissä', 'tur': 'yığmalılar mıymış'}
    twoWay_conversion(example_words[lang])
