
def word2phonemes_with_digraphs(w:[str], g2p_mapping:dict, allowed_phoneme_tokens:[str]) -> [str]: # g2p_mapping was originally called langs_properties[lang][0]
    # convert the graphemes to a list of phonemes according to the langauge's digraphs
    # g2p_dict = langs_properties[lang][0]
    digraphs = list(filter(lambda g: len(g) == 2, g2p_mapping.keys()))
    phonemes, i, flag = [], 0, False
    while i < len(w):
        if i < len(w)-1 and w[i]+w[i+1] in digraphs:
            phoneme_token = g2p_mapping[w[i] + w[i + 1]]
            i += 1
        else:
            phoneme_token = g2p_mapping[w[i]]
        if phoneme_token not in allowed_phoneme_tokens: # need to decompose to real phonemes
            phoneme_token = list(phoneme_token)
        phonemes.extend(phoneme_token if type(phoneme_token) == list else [phoneme_token])
        i += 1
    return phonemes


def word2phonemes_with_trigraphs(w:[str], g2p_mapping:dict, allowed_phoneme_tokens:[str]) -> [str]: # g2p_mapping was originally called langs_properties[lang][0]
    # convert the graphemes to a list of phonemes according to the langauge's trigraphs & digraphs
    # g2p_dict = langs_properties[lang][0]
    digraphs = list(filter(lambda x: len(x)==2, g2p_mapping.keys()))
    trigraphs = list(filter(lambda x: len(x)==3, g2p_mapping.keys()))
    phonemes, i, flag = [], 0, False
    while i < len(w):
        if i < len(w)-2 and w[i]+w[i+1]+w[i+2] in trigraphs:
            phoneme_token = g2p_mapping[w[i]+w[i+1]+w[i+2]]
            i += 2
        elif i < len(w)-1 and w[i]+w[i+1] in digraphs:
            phoneme_token = g2p_mapping[w[i] + w[i + 1]]
            i += 1
        else:
            phoneme_token = g2p_mapping[w[i]]
        if phoneme_token not in allowed_phoneme_tokens: # need to decompose to real phonemes
            phoneme_token = list(phoneme_token)
        phonemes.extend(phoneme_token if type(phoneme_token) == list else [phoneme_token])
        i += 1
    return phonemes

def phonemes2graphemes_with_doubles(w:[str], p2g_mapping:dict) -> [str]:
    phoneme_doubles = list(filter(lambda x: len(x) == 2, p2g_mapping.keys()))
    graphemes, i, flag = [], 0, False
    while i < len(w):
        if i < len(w)-1 and w[i]+w[i+1] in phoneme_doubles:
            grapheme_token = p2g_mapping[w[i] + w[i + 1]]
            i += 1
        else:
            grapheme_token = p2g_mapping[w[i]]
        grapheme_token = list(grapheme_token)
        graphemes.extend(grapheme_token if type(grapheme_token) == list else [grapheme_token])
        i += 1
    return graphemes


import json
phonemes_dictionary = json.load(open("phonemes.json", encoding='utf8'))
vowel_phonemes = phonemes_dictionary['vowels'].keys()
single_phonemes = list(phonemes_dictionary['consonants'].keys()) + list(vowel_phonemes) + [p+'ː' for p in vowel_phonemes]
single_phonemes.sort()
single_phonemes = list(filter(lambda x: x not in {'ɛ͡v', 'ŋŋ', 'ʃt', 'ja', 'ju', 'k͡s'}, single_phonemes))
# print(len(single_phonemes))
# print(single_phonemes)


# alphabet = ['ö', 'öö', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ь', 'ю', 'я']
# phonemes = ['ø', 'øː', 'a', 'b', 'v', 'ɡ', 'd', 'ɛ', 'ʒ', 'z', 'i', 'j', 'k', 'l', 'm', 'n', 'ɔ', 'p', 'r', 's', 't', 'u', 'f', 'x', 't͡s', 't͡ʃ', 'ʃ', 'ʃt', 'ɤ', 'j', 'ju', 'ja']

# hun:
# alphabet = ['a', 'á', 'b', 'c', 'cs', 'd', 'dz', 'dzs', 'e', 'é', 'f', 'g', 'gy', 'h', 'i', 'í', 'j', 'k', 'l', 'ly', 'm', 'n', 'ny', 'o', 'ó', 'ö', 'ő', 'p', 'r', 's', 'sz', 't', 'ty', 'u', 'ú', 'ü', 'ű', 'v', 'w', 'x', 'y', 'z', 'zs']
# phonemes = ['ɒ', 'aː', 'b', 't͡s', 't͡ʃ', 'd', 'd͡z', 'd͡ʒ', 'ɛ', 'eː', 'f', 'ɡ', 'ɟ', 'h', 'i', 'iː', 'j', 'k', 'l', 'ʎ', 'm', 'n', 'ɲ', 'o', 'oː', 'ø', 'øː', 'p', 'r', 'ʃ', 's', 't', 'c', 'u', 'uː', 'y', 'yː', 'v', 'w', 'ks', 'i', 'z', 'ʒ']

alphabet = ['dz', 'щ', 'a', 'è', 'é', 'e', 'i', 'o', 'u', 'y', 'ä', 'ö', 'b', 'c', 'd', 'f', 'g', 'ng', 'nk', 'h', 'j', 'k', 'l', 'm', 'n',
                'p', 'q', 'r', 's', 'š', 't', 'v', 'w', 'x', 'z', 'ž', 'å', 'aa', 'ee', 'ii', 'oo', 'uu', 'yy', 'ää', 'öö']
phonemes = ['d͡z', 'ʃt', 'ɑ', 'e', 'e', 'e', 'i', 'o', 'u', 'y', 'a', 'ø', 'b', 's', 'd', 'f', 'ɡ', 'ŋŋ', 'ŋ', 'h', 'j', 'k', 'l', 'm', 'n',
                'p', 'k', 'r', 's', 'ʃ', 't', 'v', 'v', 'ks', 't͡s', 'ʒ', 'oː', 'ɑː', 'eː', 'iː', 'oː', 'uː', 'yː', 'aː', 'øː']



d = dict(zip(alphabet, phonemes))
phon_d = dict(zip(phonemes, alphabet))

# w = list('найяснюотщööо') # bul
# w = list('eéfdzgycsklynndzso') # hun
w = list('bщvnmngodzsnkoxeööj')
print(f"w = {w}")
ps = word2phonemes_with_digraphs(w, d, single_phonemes)
print(f"ph= {ps}")
w2 = phonemes2graphemes_with_doubles(ps, phon_d)
print(f"w2= {w2}")
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
print(f"ED = {editDistance(w,w2)}")