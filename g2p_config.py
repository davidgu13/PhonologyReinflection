__author__ = "David Guriel"
import json
import unicodedata

place = ['labial', 'dental', 'alveolar', 'velarized-alveolar', 'post-alveolar', 'velar', 'uvular', 'glottal', 'palatal'] # 0-8
manner = ['nasal', 'plosive', 'fricative', 'affricate', 'trill', 'tap', 'lateral', 'approximant', 'implosive'] # 9-17
voice = ['voiceless', 'voiced', 'ejective', 'aspirated'] # 18-21
# Vowels features:
height = ['open', 'open-mid', 'mid', 'close-mid', 'close'] # 22-26
backness = ['front', 'back', 'central'] # 27-29
roundness = ['rounded', 'unrounded'] # 30-31
length = ['long'] # only for vowels; no occurence means short # 32
general_punctuations = [' ', '-', "'", "̇", '.'] # 33-39

phon_features = place + manner + voice + height + backness + roundness + length + general_punctuations
idx2feature = dict(enumerate(phon_features))
feature2idx = {v:k for k, v in idx2feature.items()} # => {'labial':0,...,'nasal':6,...,'front':18,'back':19}

# for writing the dictionaries, use the command: json.dump({"vowels":p2f_vowels_dict, "consonants":p2f_consonants_dict}, open("phonemes.json","w",encoding='utf8'), indent=2)
phonemes = json.load(open("phonemes.json", encoding='utf8'))
p2f_consonants = {k:tuple(v) for k,v in phonemes['consonants'].items()}
p2f_vowels     = {k:tuple(v) for k,v in phonemes['vowels'].items()}
p2f_vowels.update({ k+'ː': v+('long',) for k,v in p2f_vowels.items()}) # account for long vowels (and double their number)
general_punctuations_dict = dict(zip(general_punctuations, general_punctuations))
p2f_dict = {**p2f_vowels, **p2f_consonants, **general_punctuations_dict}
f2p_dict = {v:k for k,v in p2f_dict.items()}


# region definedLangs
# region Georgian - kat
kat_alphabet = ['ა', 'ბ', 'გ', 'დ', 'ე', 'ვ', 'ზ', 'თ', 'ი', 'კ', 'ლ', 'მ', 'ნ', 'ო', 'პ', 'ჟ', 'რ', 'ს', 'ტ', 'უ', 'ფ', 'ქ', 'ღ', 'ყ', 'შ', 'ჩ', 'ც', 'ძ', 'წ', 'ჭ', 'ხ', 'ჯ', 'ჰ']
kat_phonemes = ['ɑ', 'b', 'ɡ', 'd', 'ɛ', 'v', 'z', 'tʰ', 'i', 'kʼ', 'l', 'm', 'n', 'ɔ', 'pʼ', 'ʒ', 'r', 's', 'tʼ', 'u', 'pʰ', 'kʰ', 'ɣ', 'qʼ', 'ʃ', 't͡ʃʰ', 't͡sʰ', 'd͡z', 't͡sʼ', 't͡ʃʼ', 'x', 'd͡ʒ', 'h']
kat_g2p_dict = dict(zip(kat_alphabet, kat_phonemes))
kat_components = (kat_g2p_dict, None, None)
# endregion Georgian - kat


# region Swahili - swc
swc_alphabet = ['a', 'e', 'i', 'o', 'u',  'b', 'ch', 'd', 'dh', 'f', 'g', 'gh', 'h', 'j', 'k', 'kh', 'l', 'm', 'n', 'ng', "ng'", 'ny', 'p', 'r', 's', 'sh', 't', 'th', 'v', 'w', 'y', 'z']
swc_phonemes = ['ɑ', 'ɛ', 'i', 'ɔ', 'u',  'ɓ', 't͡ʃ', 'ɗ', 'ð', 'f', 'ɠ', 'ɣ', 'h', 'ʄ', 'k', 'x', 'l', 'm', 'n', 'ɡ', 'ŋ', 'ɲ', 'p', 'r', 's', 'ʃ', 't', 'θ', 'v', 'w', 'j', 'z']
swc_g2p_dict = dict(zip(swc_alphabet, swc_phonemes))
def swc_word2phonemes(w:[str]):
    return word2phonemes_with_trigraphs(w, lang='swc')
swc_components = (swc_g2p_dict, swc_word2phonemes, None)
# endregion Swahili - swc


# region Albanian - sqi
sqi_alphabet = ['a', 'b', 'c', 'ç', 'd', 'dh', 'e', 'ë', 'f', 'g', 'gj', 'h', 'i', 'j', 'k', 'l', 'll', 'm', 'n', 'nj', 'o', 'p', 'q', 'r', 'rr', 's', 'sh', 't', 'th', 'u', 'v', 'x', 'xh', 'y', 'z', 'zh']
sqi_phonemes = ['a', 'b', 't͡s', 't͡ʃ', 'd', 'ð', 'ɛ', 'ə', 'f', 'ɡ', 'ɟ͡ʝ', 'h', 'i', 'j', 'k', 'l', 'ɫ', 'm', 'n', 'ɲ', 'ɔ', 'p', 'c', 'ɹ', 'r', 's', 'ʃ', 't', 'θ', 'u', 'v', 'd͡z', 'd͡ʒ', 'y', 'z', 'ʒ']
sqi_g2p_dict = dict(zip(sqi_alphabet, sqi_phonemes))
def sqi_word2phonemes(w:[str]):
    return word2phonemes_with_digraphs(w, lang='sqi')
sqi_components = (sqi_g2p_dict, sqi_word2phonemes, None)
# endregion Albanian - sqi


# region Latvian - lav
lav_alphabet = ['a', 'ā', 'e',  'ē', 'i',  'ī', 'í', 'o', 'u',  'ū', 'b',  'c',  'č', 'd', 'dz', 'dž', 'f', 'g', 'ģ', 'h', 'j', 'k', 'ķ', 'l', 'ļ', 'm', 'n', 'ņ', 'p', 'r', 's', 'š', 't', 'v', 'z', 'ž']
lav_phonemes = ['ɑ', 'ɑː', 'e', 'eː', 'i', 'iː', 'iː', 'o', 'u', 'uː', 'b', 't̪͡s̪', 't͡ʃ', 'd̪', 'd̪͡z̪', 'd͡ʒ', 'f', 'ɡ', 'ɟ', 'x', 'j', 'k', 'c', 'l', 'ʎ', 'm', 'ŋ', 'ɲ', 'p', 'r', 's', 'ʃ', 't̪', 'v', 'z', 'ʒ']
lav_g2p_dict = {**dict(zip(lav_alphabet, lav_phonemes)), **general_punctuations_dict}
lav_p2g_dict = {**dict(zip(lav_phonemes, lav_alphabet)), **general_punctuations_dict}
def lav_phonemes2word(phonemes:[str]):
    return ['ī' if p=='iː' else lav_p2g_dict[p] for p in phonemes] # just never map /iː/ to 'í'
lav_components = (lav_g2p_dict, None, lav_phonemes2word)
# endregion Latvian - lav


# region Bulgarian - bul
bul_alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ь', 'ю', 'я']
bul_phonemes = ['a', 'b', 'v', 'ɡ', 'd', 'ɛ', 'ʒ', 'z', 'i', 'j', 'k', 'l', 'm', 'n', 'ɔ', 'p', 'r', 's', 't', 'u', 'f', 'x', 't͡s', 't͡ʃ', 'ʃ', 'ʃt', 'ɤ', 'j', 'ju', 'ja']
bul_g2p_dict = {**dict(zip(bul_alphabet, bul_phonemes)), **general_punctuations_dict}
bul_p2g_dict = {**dict(zip(bul_phonemes, bul_alphabet)), **general_punctuations_dict}
def bul_phonemes2word(phonemes:[str]):
    return ['й' if p=='j' else bul_p2g_dict[p] for p in phonemes] # just never map /j/ to 'ь' (151 out of 55731)
bul_components = (bul_g2p_dict, None, bul_phonemes2word)
# endregion Bulgarian - bul


# region Hungarian - hun
hun_alphabet = ['a', 'á', 'b', 'c', 'cs', 'd', 'dz', 'dzs', 'e', 'é', 'f', 'g', 'gy', 'h', 'i', 'í', 'j', 'k', 'l', 'ly', 'm', 'n', 'ny', 'o', 'ó', 'ö', 'ő', 'p', 'r', 's', 'sz', 't', 'ty', 'u', 'ú', 'ü', 'ű', 'v', 'w', 'x', 'y', 'z', 'zs']
hun_phonemes = ['ɒ', 'aː', 'b', 't͡s', 't͡ʃ', 'd', 'd͡z', 'd͡ʒ', 'ɛ', 'eː', 'f', 'ɡ', 'ɟ', 'h', 'i', 'iː', 'j', 'k', 'l', 'ʎ', 'm', 'n', 'ɲ', 'o', 'oː', 'ø', 'øː', 'p', 'r', 'ʃ', 's', 't', 'c', 'u', 'uː', 'y', 'yː', 'v', 'w', 'k͡s', 'i', 'z', 'ʒ']
hun_g2p_dict = {**dict(zip(hun_alphabet, hun_phonemes)), **general_punctuations_dict}
hun_p2g_dict = {**dict(zip(hun_phonemes, hun_alphabet)), **general_punctuations_dict}
def hun_word2phonemes(w:[str]):
    # w = w.replace('|or|', "")
    return word2phonemes_with_trigraphs(w, 'hun')
def hun_phonemes2word(phonemes:[str]):
    return ['i' if p=='i' else hun_p2g_dict[p] for p in phonemes] # just never map /i/ to 'y'
hun_components = (hun_g2p_dict, hun_word2phonemes, hun_phonemes2word)
# endregion Hungarian - hun


# region Turkish - tur
tur_alphabet = ['a', 'b', 'c', 'ç', 'd', 'e', 'f', 'g', 'ğ', 'h', 'ı', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'ö', 'p', 'r', 's', 'ş', 't', 'u', 'ü', 'v', 'y', 'z', 'w', 'x' , 'â', 'î', 'û']
tur_phonemes = ['a', 'b', 'd͡ʒ', 't͡ʃ', 'd', 'ɛ', 'f', 'ɡ', 'j', 'h', 'ɯ', 'i', 'ʒ', 'k', 'l', 'm', 'n', 'o', 'œ', 'p', 'ɾ', 's', 'ʃ', 't', 'u', 'y', 'v', 'j', 'z', 'w', 'k͡s', 'aː', 'iː', 'uː']
tur_g2p_dict = {**dict(zip(tur_alphabet, tur_phonemes)), **general_punctuations_dict}
tur_p2g_dict = {**dict(zip(tur_phonemes, tur_alphabet)), **general_punctuations_dict}
def lengthen_last_vowel_phoneme(phonemes_list):
    phonemes_list[-1]+='ː'
    return phonemes_list
def feature_in_letter(feature:str, some_g2p_dict:[str], g:str): return feature in p2f_dict[some_g2p_dict[g]]
turkish_vowels = {'a', 'e', 'i', 'o', 'u', 'ı', 'ö', 'ü', 'â', 'î', 'û'}
def is_tur_vowel(c): return c in turkish_vowels
def tur_word2phonemes(w:[str]): # mostly for handling ğ
    w = ''.join(w)
    w = w.casefold() # lowercasing
    graphemes, phonemes, i = list(w), [], 0
    while i < len(w):
        c, resulted_phoneme1 = graphemes[i], ''
        if c=='ğ':
            assert graphemes[i - 1] in turkish_vowels # must obey the regex [aeiouıöüâîû]ğ
            if i==len(w)-1 or graphemes[i+1]==' ': # last letter before whitespace
                phonemes = lengthen_last_vowel_phoneme(phonemes)
            else:
                trigraph = graphemes[i - 1: i + 2]
                if trigraph[0]==trigraph[2]:
                    assert trigraph[0] not in {'â', 'î', 'û'} # because they're already long vowels!
                    phonemes = lengthen_last_vowel_phoneme(phonemes)
                    i+=1
                elif feature_in_letter('front', tur_g2p_dict, trigraph[0]): # follows a front vowel # להוסיף שצריך להיות אחרי e
                    resulted_phoneme= 'j'
                # otherwise just ignore the 'ğ'
        else:
            resulted_phoneme = tur_g2p_dict[c]
        if resulted_phoneme!='':
            phonemes.append(resulted_phoneme)
        i+=1
    return phonemes
def tur_phonemes2word(phonemes:[str]): # in ambiguitive situations, the major vote was chosen.
    graphemes = []
    for i,p in enumerate(phonemes):
        if p=='j':
            g = 'y'
        elif p=='aː' in p:
            g = 'â'
        elif p=='uː' in p:
            g = ['u', 'ğ', 'u']
        elif 'ː' in p: # a long vowel
            g = [tur_p2g_dict[p[0]], 'ğ']
            # if not (i==len(phonemes)-1 or phonemes[i+1]==' '):
            #     g += tur_p2g_dict[p[0]]
        else:
            g = tur_p2g_dict[p]
        graphemes.extend(g if type(g)==list else [g])
    return graphemes
tur_components = (tur_g2p_dict, tur_word2phonemes, tur_phonemes2word)
# endregion Turkish - tur


# region Finnish - fin
fin_alphabet = ['a', 'è', 'é', 'e', 'i', 'o', 'u', 'y', 'ä', 'ö', 'b', 'c', 'd', 'f', 'g', 'ng', 'nk', 'h', 'j', 'k', 'l', 'm', 'n',
                'p', 'q', 'r', 's', 'š', 't', 'v', 'w', 'x', 'z', 'ž', 'å', 'aa', 'ee', 'ii', 'oo', 'uu', 'yy', 'ää', 'öö']
fin_phonemes = ['ɑ', 'e', 'e', 'e', 'i', 'o', 'u', 'y', 'a', 'ø', 'b', 's', 'd', 'f', 'ɡ', 'ŋŋ', 'ŋ', 'h', 'j', 'k', 'l', 'm', 'n',
                'p', 'k', 'r', 's', 'ʃ', 't', 'v', 'v', 'k͡s', 't͡s', 'ʒ', 'oː', 'ɑː', 'eː', 'iː', 'oː', 'uː', 'yː', 'aː', 'øː']
fin_g2p_dict = {**dict(zip(fin_alphabet, fin_phonemes)), **general_punctuations_dict}
fin_p2g_dict = {**dict(zip(fin_phonemes, fin_alphabet)), **general_punctuations_dict}
def fin_word2phonemes(w:[str]):
    w = [c.replace('\xa0', ' ') for c in w]
    return word2phonemes_with_digraphs(w, 'fin')
def fin_phonemes2word(phonemes:[str]):
    graphemes = []
    for p in phonemes:
        if p == 'e':
            g = 'e' # ignore 'é' and 'è'
        elif p == 'oː':
            g = ['o', 'o'] # ignore 'å'
        elif p == 'k':
            g = 'k' # ignore 'q'
        elif p == 's':
            g = 's' # ignore 'c'
        elif p == 'v':
            g = 'v' # ignore 'w'
        elif p == 'ɑː':
            g = ['a', 'a']
        else:
            g = fin_p2g_dict[p]
        graphemes.extend(g if type(g)==list else [g])
    return graphemes

fin_components = (fin_g2p_dict, fin_word2phonemes, fin_phonemes2word)
# endregion Finnish - fin


# region Armenian - hye
# Not finished! Didn't add this lang bc it has too many exceptions for 'ե', 'ո', 'ու' and 'և'. Also there are ligatures. That's just too complex.
# hye_alphabet = ['ա', 'բ', 'գ', 'դ', 'ե', 'զ', 'է', 'ը', 'թ', 'ժ', 'ի', 'լ', 'խ', 'ծ', 'կ', 'հ', 'ձ', 'ղ', 'ճ', 'մ', 'յ', 'ն', 'շ', 'ո', 'չ', 'պ', 'ջ', 'ռ', 'ս', 'վ', 'տ', 'ր', 'ց', 'ու', 'փ', 'ք', 'և', 'օ', 'ֆ']
# hye_phonemes = ['ɑ', 'b', 'ɡ', 'd', 'ɛ', 'z', 'ɛ', 'ə', 'tʰ', 'ʒ', 'i', 'l', 'χ', 't͡s', 'k', 'h', 'd͡z', 'ʁ', 't͡ʃ', 'm', 'j', 'n', 'ʃ', 'ɔ', 't͡ʃʰ', 'p', 'd͡ʒ', 'r', 's', 'v', 't', 'ɾ', 't͡sʰ', 'u', 'pʰ', 'kʰ', 'ɛ͡v', 'o', 'f']
# hye_g2p_dict = dict(zip(hye_alphabet, hye_phonemes))
# def hye_word2phonemes(w:[str]):
#     special_e_words_g = ['եմ', 'ես', 'ենք', 'եք', 'են'] # [['ե', 'մ'], ['ե', 'ս'], ['ե', 'ն', 'ք'], ['ե', 'ք'], ['ե', 'ն']]
#     special_e_words_p = [['ɛ', 'm'], ['ɛ', 's'], ['ɛ', 'n', 'kʰ'], ['ɛ', 'kʰ'], ['ɛ', 'n']]
#     p, phonemes = '', []
#     for i,g in enumerate(w):
#         if g == 'ե' and i==0:
#             if ''.join(w) in special_e_words_g:
#                 p = 'ɛ'
#             else:
#                 p = ['j', 'ɛ']
#         elif g == 'ո' and i==0: p = ['v', 'ɔ']
#         elif g == 'և' and i==0: p = ['j', 'ɛ', 'v']
#         else:
#             p = hye_g2p_dict[g]
#         phonemes.extend(p if type(p)==list else [p])
#     return phonemes
# # Not finished!
# def hye_phonemes2word(phonemes:[str]):
#     graphemes = []
#     for p in phonemes:
#         if p == 'ɛ':
#             g = 'ե' # ignore 'է'
#         # elif True:
#         #     pass
#         else:
#             g = tur_p2g_dict[p]
#         graphemes.extend(g if type(g)==list else [g])
#     return graphemes
# hye_components = (hye_g2p_dict, hye_word2phonemes, hye_phonemes2word)
# endregion Armenian - hye


# # endregion definedLangs

langs_properties = {'kat': kat_components, 'tur': tur_components, 'swc': swc_components,
                    'sqi': sqi_components, 'bul': bul_components, # 'hye': hye_components,
                    'hun': hun_components, 'lav': lav_components, 'fin': fin_components,}

def word2phonemes_with_digraphs(w:[str], lang:str):
    # break the word to graphemes given some digraphs and convert to a list of phonemes
    g2p_dict = langs_properties[lang][0]
    digraphs = list( filter(lambda x: len(x)==2, g2p_dict.keys()) )
    if lang=='sqi': w = list(filter(lambda g:g!="'", w)) # appears in the data only as part of "për t'u ..." (NFIN)
    phonemes = []
    i, flag = 0, False
    while i < len(w):
        if i<len(w)-1 and w[i]+w[i+1] in digraphs: # the index is before the last character (no risk of exceptions!)
            phonemes.append(g2p_dict[w[i]+w[i+1]])
            i+=2
        else:
            phonemes.append(g2p_dict[w[i]])
            i+=1
    return phonemes
def word2phonemes_with_trigraphs(w:[str], lang:str):
    # break the word to graphemes given some trigraphs and digraphs and convert to a list of phonemes
    g2p_dict = langs_properties[lang][0]
    digraphs = list( filter(lambda x: len(x)==2, g2p_dict.keys()) )
    trigraphs = list( filter(lambda x: len(x)==3, g2p_dict.keys()) )
    if lang=='sqi': w = list(filter(lambda g:g!="'", w)) # appears in the data only as part of "për t'u ..." (NFIN)
    phonemes = []
    i, flag = 0, False
    while i < len(w):
        if i<len(w)-2 and w[i]+w[i+1]+w[i+2] in trigraphs:
            phonemes.append(g2p_dict[w[i]+w[i+1]+w[i+2]])
            i+=3
        if i<len(w)-1 and w[i]+w[i+1] in digraphs: # the index is before the last character (no risk of exceptions!)
            phonemes.append(g2p_dict[w[i]+w[i+1]])
            i+=2
        else:
            phonemes.append(g2p_dict[w[i]])
            i+=1
    return phonemes

def is_g2p_1to1(d:dict): return len(d.values())==len(set(d.values()))
def are_there_unincluded_phonemes(lang_phonemes:[str]) -> [str]: return [p for p in lang_phonemes if p not in p2f_dict.keys()]


# region manually inserting g-p pairs
# (copy that section to the console and insert; once done, copy back to the script.
# k,v, d = 'a', 'ɑ', {} # initial pair
# while (k,v)!=('',''):
#     d[k]=v
#     k,v = input("insert k"), input("insert v")
# endregion manually inserting g-p pairs:
