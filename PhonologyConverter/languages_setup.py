from itertools import chain
from editdistance import eval as edit_distance_eval
from typing import List, Union, Tuple

from PhonologyConverter.g2p_config import idx2feature, feature2idx, p2f_dict, f2p_dict, langs_properties, punctuations

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
    def __init__(self, lang_name: str, graphemes2phonemes:dict, max_phoneme_size: int,
                 phon_use_attention: bool, manual_word2phonemes=None, manual_phonemes2word=None):
        self._name = lang_name
        self._graphemes2phonemes = graphemes2phonemes
        self._graphemes2phonemes.update(dict(zip(punctuations, punctuations)))
        self._phonemes2graphemes = {v:k for k, v in self._graphemes2phonemes.items()} # _graphemes2phonemes.reverse

        self._alphabet = list(self._graphemes2phonemes.keys()) # the graphemes of the language
        self._phonemes = list(self._graphemes2phonemes.values())

        self._manual_word2phonemes = manual_word2phonemes
        self.manual_phonemes2word = manual_phonemes2word

        self.max_phoneme_size = max_phoneme_size
        self.phon_use_attention = phon_use_attention

    def get_lang_name(self): return self._name
    def get_lang_alphabet(self): return self._alphabet
    def get_lang_phonemes(self): return self._phonemes

    def word2phonemes(self, word:str, mode:str) -> Union[List[List[int]], List[str]]:
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
                feats.extend(['NA']*(self.max_phoneme_size-len(feats)))
                if self.phon_use_attention:
                    feats.append(p)
                features.append(tuple(feats))
            features = tuple_of_phon_tuples2phon_sequence(features)
            return features

    def phonemes2word(self, phonemes: [[str]], mode:str) -> str:
        """
        Convert a list of phoneme tuples to a word (sequence of graphemes)
        :param phonemes: [(,,), (,,), (,,), ...] or (*IPA symbols*)
        :param mode: can be either 'features' or 'phonemes' (see more above).
        :return: word
        """
        assert mode in {'features', 'phonemes'}, f"Mode {mode} is invalid"

        if mode=='phonemes':
            if self.manual_phonemes2word:
                graphemes = self.manual_phonemes2word(phonemes)
            else:
                graphemes = [self._phonemes2graphemes[p] for p in phonemes]
        else: # mode=='features'
            if self.phon_use_attention:
                phoneme_tokens = [f_tuple[-1] for f_tuple in phonemes]
            else:
                phoneme_tokens = []
                for f_tuple in phonemes:
                    f_tuple = tuple([idx2feature[int(i)] for i in f_tuple if i != 'NA'])
                    p = f2p_dict.get(f_tuple)
                    if p is None or p not in self._phonemes: p = "#" # the predicted bundle is illegal or doesn't exist in this language
                    phoneme_tokens.append(p)
            graphemes = self.phonemes2word(phoneme_tokens, 'phonemes')
        return ''.join(graphemes)

# For debugging purposes:
def two_way_conversion(w):
    print(f"PHON_USE_ATTENTION, lang = {hp.PHON_USE_ATTENTION}, '{hp.lang}'")
    print(f"w = {w}")
    ps = langPhonology.word2phonemes(w, mode='phonemes')
    feats = langPhonology.word2phonemes(w, mode='features')
    print(f"phonemes = {ps}\nfeatures = {feats}")

    p2word = langPhonology.phonemes2word(ps, mode='phonemes')
    print(f"p2word: {p2word}\nED(w, p2word) = {edit_distance_eval(w, p2word)}")

    feats = [f.split(',') for f in ','.join(feats).split(',$,')]
    f2word = langPhonology.phonemes2word(feats, mode='features')
    print(f"f2word: {f2word}\nED(w, f2word) = {edit_distance_eval(w, f2word)}")

# Change this to True only when debugging the g2p/p2g conversions!
debugging_mode = False
import hyper_params_config as hp
if debugging_mode:
    hp.PHON_USE_ATTENTION, hp.lang = False, 'fin'
MAX_FEAT_SIZE = max([len(p2f_dict[p]) for p in langs_properties[hp.lang][0].values() if p in p2f_dict]) # composite phonemes aren't counted in that list
langPhonology = LanguageSetup(hp.lang, langs_properties[hp.lang][0], langs_properties[hp.lang][1], langs_properties[hp.lang][2])

if __name__ == '__main__':
    # made-up words to test the correctness of the g2p/p2g conversions algorithms (for debugging purposes):
    example_words = {'kat': 'არ მჭირდ-ებოდყეტ', 'swc': "magnchdhe-ong jwng'a", 'sqi': 'rdhëije rrçlldgj-ijdhegnjzh', 'lav': 'abscā t-raķkdzhēļšanģa',
                     'bul': 'най-ясюногщжто', 'hun': 'hűdályiokró- l eéfdzgycsklynndzso nyoyaxy', 'tur': 'yığmalılksar mveğateğwypûrtâşsmış', 'fin': 'ixlmksnngvnk- èeé aatööböyynyissä'}
    two_way_conversion(example_words[hp.lang])
