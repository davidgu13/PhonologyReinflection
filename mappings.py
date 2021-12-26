
def word2phonemes_with_digraphs(w:[str], g2p_dict:dict):
    # break the word to graphemes given some digraphs and convert to a list of phonemes
    # g2p_dict = langs_properties[lang][0]
    digraphs = list( filter(lambda x: len(x)==2, g2p_dict.keys()) )
    # if lang=='sqi': w = list(filter(lambda g:g!="'", w)) # appears in the data only as part of "për t'u ..." (NFIN)
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
def word2phonemes_with_trigraphs(w:[str], g2p_dict:dict):
    # break the word to graphemes given some trigraphs and digraphs and convert to a list of phonemes
    # g2p_dict = langs_properties[lang][0]
    digraphs = list( filter(lambda x: len(x)==2, g2p_dict.keys()) )
    trigraphs = list( filter(lambda x: len(x)==3, g2p_dict.keys()) )
    # if lang=='sqi': w = list(filter(lambda g:g!="'", w)) # appears in the data only as part of "për t'u ..." (NFIN)
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

def src_tokens2trg_tokens_with_doubles(w:[str], src_2_trg_mapping:dict):
    src_doubles = list(filter(lambda x: len(x) == 2, src_2_trg_mapping.keys()))
    w_trg, i, flag = [], 0, False
    while i < len(w):
        current_character, double_candidate = w[i], w[i]+w[i+1]
        if i < len(w)-1 and double_candidate in src_doubles:
            w_trg.append(src_2_trg_mapping[double_candidate])
            i += 2
        else:
            w_trg.append(src_2_trg_mapping[current_character])
            i += 1
    return w_trg

def word2phonemes_with_digraphs_new(w:[str], g2p_dict:dict):
    pass # Call src_tokens2trg_tokens_with_doubles