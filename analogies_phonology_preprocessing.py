import os
from more_itertools import flatten
from PhonologyConverter.languages_setup import langPhonology, LanguageSetup, joinit
from data2samples_converter import Data2SamplesConverter
import hyper_params_config as hp
from typing import List

def is_features_bundle(e):
    if hp.lang == 'kat':
        return hp.POS in e # in Georgian there exist features like 's1', 'oPL' etc.
    else:
        return str.isupper(e) and hp.POS in e # assuming no lower-case features exist in other languages.

def remove_double_dollars(sequence:[str]):
    # used during the conversion to graphemes-mode
    if sequence[-1]=='$': del sequence[-1] # because it's irrelevant for the morphological evaluation
    if sequence[0]=='$': del sequence[0]
    # Removing unwanted commas and dollars from each token:
    s = ','.join(sequence).split(',$,')
    s = [e.strip(',$') for e in s]
    stripped_seq = ',$,'.join(s).split(',') # if there aren't any '$' issues, stripped_seq==seq
    return stripped_seq

class PhonologyDecorator:
    # Implements phonology logic while accounting for Analogies format. Use it only if the input & output aren't both graphemes
    def __init__(self, phonology_converter: LanguageSetup):
        super().__init__()
        self.phonology_converter = phonology_converter

    def line2phon_line(self, src_list: str, trg_form: str):
        """
        Takes src_list and trg_form, and converts their words to a phonological representation - one of the 3 options.
        If one of them is '', then it's returned as is.
        Used for preprocessing.
        :param src_list: a string of the format 'e1,+,e2,+,...,+,en', where e_i can be either a features bundle or a word (comma-separated as-well)
        :param trg_form:
        :return:
        """
        if src_list:
            src_list_split = src_list.split(',+,')
            src_list_separated, new_src_list = [e.replace(',',';' if is_features_bundle(e) else '') for e in src_list_split], []
            for e in src_list_separated:
                if ';' in e:
                    new_src_list.append(e.split(';'))
                else:
                    new_src_list.append(self.phonology_converter.word2phonemes(e, mode=hp.inp_phon_type))
            new_src_list = list(flatten( joinit(new_src_list,['+']) ))
        else:
            new_src_list = src_list

        if trg_form:
            trg_form = trg_form.replace(',','')
            new_trg_form = self.phonology_obj.word2phonemes(trg_form, mode=hp.out_phon_type)
        return new_src_list, new_trg_form


    def _phon_sequence2word_extended(self, sequence, mode) -> str:
        # Handle target and prediction sequences.
        assert mode in {'features', 'phonemes'}
        if mode=='features': # type(sequence)==str
            phon_feats = sequence.split(',$,') # cannot handle more than 2 following '$' chars in a row. Not an issue for now.
            if self.phonology_obj.manual_phonemes2word and hp.PHON_USE_ATTENTION:
                new_sequence = self.phonology_obj.phonemes2word([e.split(',')[-1] for e in phon_feats], mode='phonemes')
            else:
                new_sequence = self.phonology_obj.phonemes2word([p.split(',') for p in phon_feats], mode='features')
        else: # mode=='phonemes' => type(sequence)==[str]
            new_sequence = self.phonology_obj.phonemes2word(sequence, mode='phonemes')
        return new_sequence

        return new_src_list, new_trg_form

    def _phon_src2word_src(self, src_phon: List[str], mode: str):
        # Handle the source string
        assert src_phon.count(',+,') >= 2 # at least 3 elements
        elements, new_src_list = src_phon.split(',+,'), []
        for e in elements:
            if '$' in e: # 'features'
                new_e = self._phon_sequence2word_extended(e, mode='features')
            elif set(e.split(',')).issubset(self.phonology_obj.get_lang_phonemes()): # 'phonemes'
                new_e = self._phon_sequence2word_extended(e.split(','), mode='phonemes')
            else: # a string of morphological features
                new_e = e.replace(',',';')
            new_src_list.append(new_e)
        return new_src_list


    def phon_sample2morph_sample(self, src: List[str], trg: List[str], pred: List[str],
                     inp_mode: str = hp.inp_phon_type, out_mode: str = hp.out_phon_type) -> (List[str], str, str):
        # Convert the source, target & prediction elements (if needed)
        assert inp_mode in {'graphemes', 'phonemes', 'features'} and out_mode in {'graphemes', 'phonemes', 'features'}
        # Handle source
        if inp_mode=='graphemes':
            new_src = [e.replace(',',';' if is_features_bundle(e) else '') for e in ','.join(src).split(',+,')]
        else: # 'phonemes' or 'features'
            new_src = self._phon_src2word_src(src, inp_mode)

        # Handle target, then handle prediction
        if out_mode=='graphemes':
            new_trg = trg
            new_pred = pred
        else:
            if out_mode=='features': pred = remove_double_dollars(pred) # TODO: move the prediction cleaning to inside phonemes2word, being optional
            new_trg = self.phonology_converter.phonemes2word(trg, out_mode) # convert to words (graphemes)
            new_pred = self.phonology_converter.phonemes2word(pred, out_mode) # convert to words (graphemes)
        return new_src, new_trg, new_pred

    # Do not implement a method for writing the processed data to files! Make sure to only use it at the preprocessing part!

phonology_decorator = PhonologyDecorator(langPhonology)

if __name__ == '__main__':
    # For debugging purposes
    old_dir = os.path.join(".data", "Reinflection", "kat.V", "src1_cross1")
    test_file = os.path.join(old_dir, f"kat.V.form.test.src1_cross1.tsv")
    lines = open(test_file, encoding='utf8').readlines()
    for i, l in enumerate(lines):
        if i == 20: break
        src, trg = l.strip().split('\t')
        new_src, new_trg = phonology_decorator.line2phon_line(src, trg)
        print(f"src: {src}, trg: {trg}")
        print(f"new_src: {new_src}, new_trg: {new_trg}\n")
    # If this doesn't run, it's because in hyper_params_config.py the default I-O values are g-g.
    # Try modifying them to f-f, or even f-p + default --ATTN value to True