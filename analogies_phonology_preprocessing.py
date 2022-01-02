import os
from more_itertools import flatten
from languages_setup import langPhonology, LanguageSetup, joinit
from data2samples_converter import Data2SamplesConverter
from hyper_params_config import analogy_type, training_mode, inp_phon_type, out_phon_type, POS, PHON_USE_ATTENTION

def remove_double_dollars(sequence:[str]):
    # used during the conversion to graphemes-mode
    if sequence[-1]=='$': del sequence[-1] # because it's irrelevant for the morphological evaluation
    if sequence[0]=='$': del sequence[0]
    # Removing unwanted commas and dollars from each token:
    s = ','.join(sequence).split(',$,')
    s = [e.strip(',$') for e in s]
    stripped_seq = ',$,'.join(s).split(',') # if there aren't any '$' issues, stripped_seq==seq
    return stripped_seq

class GenericPhonologyProcessing(Data2SamplesConverter):
    # Implements phonology logic while accounting for Analogies format. Use it only if the input & output aren't both graphemes
    def __init__(self, phonology: LanguageSetup):
        super().__init__()
        self.phonology_obj = phonology

    def line2phon_line_generic(self, src_list:[str], trg_form:str, convert_src=True, convert_trg=True):
        """
        Takes a line of the format ([e1, e2, ..., en], trg_form), where e_i can be either a
        features bundle or a word, and converts its words to a phonological representation - one of the 3 options.
        Used for preprocessing.
        :param src_list:
        :param trg_form:
        :param convert_src: if False, do nothing
        :param convert_trg: if False, do nothing
        :return:
        """
        if not convert_src: new_src_list = src_list
        else:
            src_list = src_list.split(',+,')
            src_list, new_src_list = [e.replace(',',';') if str.isupper(e) and POS in e else e.replace(',','') for e in src_list], []
            for i,e in enumerate(src_list):
                if ';' in e:
                    new_src_list.append(e.split(';'))
                else:
                    new_src_list.append(self.phonology_obj.word2phonemes(e, mode=inp_phon_type))
            new_src_list = list(flatten( joinit(new_src_list,['+']) ))

        if not convert_trg: new_trg_form = trg_form
        else:
            trg_form = trg_form.replace(',','')
            new_trg_form = self.phonology_obj.word2phonemes(trg_form, mode=out_phon_type)
        return new_src_list, new_trg_form


    def _phon_sequence2word_extended(self, sequence, mode) -> str:
        # Handle target and prediction sequences.
        assert mode in {'features', 'phonemes'}
        if mode=='features': # type(sequence)==str
            phon_feats = sequence.split(',$,') # cannot handle more than 2 following '$' chars in a row. Not an issue for now.
            if self.phonology_obj.manual_phonemes2word and PHON_USE_ATTENTION:
                new_sequence = self.phonology_obj.phonemes2word([e.split(',')[-1] for e in phon_feats], mode='phonemes')
            else:
                new_sequence = self.phonology_obj.phonemes2word([p.split(',') for p in phon_feats], mode='features')
        else: # mode=='phonemes' => type(sequence)==[str]
            new_sequence = self.phonology_obj.phonemes2word(sequence, mode='phonemes')
        return new_sequence

    def _phon_src2word_src_generic(self, src_phon:str):
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


    def phon_elements2morph_elements_generic(self, src:[str], trg:[str], pred:[str],
                     inp_mode:str=inp_phon_type, out_mode:str=out_phon_type) -> ([str], str, str):
        # Convert the source, target & prediction elements (if needed)
        assert inp_mode in {'graphemes', 'phonemes', 'features'} and out_mode in {'graphemes', 'phonemes', 'features'}
        # Handle source
        if inp_mode=='graphemes':
            new_src = [e.replace(',',';' if POS in e else '') for e in ','.join(src).split(',+,')]
        else: # 'phonemes' or 'features'
            src = ','.join(src)
            new_src = self._phon_src2word_src_generic(src)

        # Handle target, then handle prediction
        if out_mode=='graphemes':
            new_trg = trg
            new_pred = pred
        else:
            if out_mode=='features':
                trg = ','.join(trg)
                pred = remove_double_dollars(pred)
                pred = ','.join(pred)
            new_trg = self._phon_sequence2word_extended(trg, out_mode) # convert to words (graphemes)
            new_pred = self._phon_sequence2word_extended(pred, out_mode) # convert to words (graphemes)
        return new_src, new_trg, new_pred

    # Do not implement a method for writing the processed data to files! Make sure to only use it at the preprocessing part!


combined_phonology_processor = GenericPhonologyProcessing(langPhonology)

if __name__ == '__main__':
    old_dir = os.path.join(".data","AnalogiesData","src1_cross1")
    orig_trn_file, orig_dev_file, orig_tst_file = [f"{training_mode}sp.schema2.{e}_{analogy_type}.tsv" for e in ['train', 'dev', 'test']]
    fn = os.path.join(old_dir,orig_tst_file)
    lines = open(fn,encoding='utf8').readlines()
    for l in lines:
        src, trg = l.strip().split('\t')
        new_src, new_trg = combined_phonology_processor.line2phon_line_generic(src, trg)
