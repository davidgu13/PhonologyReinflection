import os
import random
from data2samples_converter import Data2SamplesConverter
from copy import deepcopy
from tqdm import tqdm
from hyper_params_config import analogy_type, training_mode
import codecs
random.seed(1)

def find_common_features(lemmas:[dict]) -> [str]:
    features_list = [set(lemma.keys()) for lemma in lemmas] # generalization of feats1, feats2 = set(lemma1.keys()), set(lemma2.keys())
    return set.intersection(*features_list)

def has_features(paradigm_entries: dict, features:[str]) -> bool:
    return set(features).issubset(paradigm_entries.keys())

def filter_dict_by_features(lemma_dict:dict, features:[str]) -> dict:
    """
    Filter lemma_dict (supposed to be a dict composed of train/dev/test sets reinflection samples) by given features.
    """
    return {k:v for k,v in lemma_dict.items() if has_features(v, features)}


def join_fo(w:str): return w.replace(',','')
def join_fe(w:str): return w.replace(',',';')

def spl_fe(w:str): return w.split(';')
def spl_fo(w:str): return list(w)


def read_inflection_tables(inflection_file):
    """ read a standard inflection file (of the format "lemma\tform\tfeature") and construct a standard dictionary:
     {lemma1: {feature1: form1, feature2: form2, ...}, lemma2: {feature1: form1, feature2: form2, ...}, ... } """
    D = {}
    with codecs.open(inflection_file, 'rb', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            lemma, word, tag = line.split("\t")
            if lemma not in D:
                D[lemma] = {}
            D[lemma][tag] = word
    return D

def read_reinflection_samples(file_name):
    """ Read a reinflectin-format file """
    data = []
    with open(file_name, encoding='utf8') as f:
        for line in f:
            elements = line.strip('\n').split('\t') # src_feat, src_form, trg_feat, trg_form
            assert len(elements) == 4
            data.append(tuple(elements))
    return data

def inflection_paradigms2list_and_dict(inflection_file):
    """
    :param inflection_file: a standard Inflection file.
    :return: a list of (lemma, form, feature) tuples + a dictionary of the form
             { feature1: {form1:lemma1, form2:lemma2, ...}, feature2:{form1:lemma1, form2:lemma2, ...}, ... }
    """
    inflection_paradigms = read_inflection_tables(inflection_file)
    tuples = []
    features_occurences = {}
    for lemma, feature_form_entries in inflection_paradigms.items():
        for feature, form in feature_form_entries.items():
            tuples.append((lemma, form, feature))
            if feature not in features_occurences:
                features_occurences[feature] = {}
            features_occurences[feature][form] = lemma
    return tuples, features_occurences

def group_reinflection_samples_by_lemmas(features_occurences, reinflection_file):
    """
    :param features_occurences: as described at inflection_paradigms2list_and_dict
    :param reinflection_file: a file of reinflection samples
    :return: a sub-dictionary of the one generated when applying read_inflection_tables to the corresponding inflection file
    """
    reinflection_samples = read_reinflection_samples(reinflection_file)
    inflections_subdictionary = {}
    for reinflection_sample in reinflection_samples:
        src_feat, src_form, trg_feat, trg_form = reinflection_sample
        if 'MSDR' in src_feat and 'MSDR' not in trg_feat: # Masdars might appear in 2 paradigms
            lemma = features_occurences[trg_feat][trg_form]
            # if tables_by_feats[trg_feat][trg_form] != tables_by_feats[src_feat][src_form]:
            #     print(f'sample = {s}. src_lemma = {tables_by_feats[src_feat][src_form]}, trg_lemma = {tables_by_feats[trg_feat][trg_form]}')
        else:
            lemma = features_occurences[src_feat][src_form]
        if lemma not in inflections_subdictionary:
            inflections_subdictionary[lemma] = {}
        inflections_subdictionary[lemma][src_feat] = src_form
        inflections_subdictionary[lemma][trg_feat] = trg_form
    return inflections_subdictionary

class AnalogyFunctionality(Data2SamplesConverter):
    """
    A class for generating new train-dev-test datasets based on Analogy methods. The datasets consist of the original
    datasets samples, combined with "analogised" data. The datasets proportions is pre-defined by those of the
    original datasets.

    Note: there's no difference between the form-split and the lemma-split implementations, because this separation
    is only done between the original train-dev-test samples. In fact, the auxiliary samples used for
    analogising can be used in both the train and test sets!
    """
    def __init__(self, original_files_dir, new_files_dir, inflections_file, train_file, dev_file, test_file):
        """
        :param original_files_dir: the location of train_file, dev_file, test_file
        :param new_files_dir: the location of the new analogy files to be generated
        :param inflections_file: the complete list of paradigms from which the reinflection samples were generated
        :param train_file: the name of the train reinflection samples file.
        :param dev_file: the name of the dev reinflection samples file.
        :param test_file: the name of the test reinflection samples file.
        """
        super().__init__()

        self.inflection_data_file = inflections_file
        self.new_dir = new_files_dir
        self.train_file, self.dev_file, self.test_file = [os.path.join(original_files_dir, f) for f in [train_file, dev_file, test_file]]

        # read the reinflection samples of each set:
        self.train_samples = read_reinflection_samples(self.train_file)
        self.dev_samples = read_reinflection_samples(self.dev_file)
        self.test_samples = read_reinflection_samples(self.test_file)

        _, self.features_dictionary = inflection_paradigms2list_and_dict(inflections_file)
        # print("Grouping train samples to dictionaries")
        self.train_lemmas_dictionary = group_reinflection_samples_by_lemmas(self.features_dictionary, self.train_file)
        # if self.training_mode == 'lemma': # we need them for the purpose of finding the right features.
        #     print("Grouping dev samples to dictionaries")
        #     self.dev_lemmas_d = group_reinflection_by_lemmas(self.feats_d, self.dev_file) # not sure if necessary
        #     print("Grouping test samples to dictionaries")
        #     self.tst_lemmas_d = group_reinflection_by_lemmas(self.feats_d, self.tst_file) # not sure if necessary
        # l1, l2, l3 = list(self.trn_lemmas_d.keys()), list(self.dev_lemmas_d.keys()), list(self.tst_lemmas_d.keys())
        # print(set(l1) & set(l2))
        # print(set(l1) & set(l3))
        # print(set(l2) & set(l3))
        # print(len(l1)+len(l2)+len(l3))
        self._choices = {'src2': {"str": '_src2', "data2sample": self._source_2_reinflection, "sample2data":self._source_2_sample2data, "generate": self._generate_d_source},  # {'name':(dir_suffix,src-trg line writing method, generation method)}
                         'src1_cross1': {"str": '_src1_cross1', "data2sample": self._cross1_reinflection, "sample2data":self._cross1_sample2data, "generate": self._generate_cross_1},
                         'src1_cross2': {"str": '_src1_cross2', "data2sample": self._cross2_reinflection, "sample2data":self._cross2_sample2data, "generate": self._generate_cross2}}

    def _generate_d_source(self, d=2):
        """
        :return: 3 lists of reinflection samples
        """
        assert d>1
        random.seed(1)
        trn_orig, dev_orig, tst_orig = deepcopy(self.train_samples), deepcopy(self.dev_samples), deepcopy(self.test_samples)
        orignal_samples = [trn_orig, dev_orig, tst_orig]
        new_samples, bad_samples = [], [] # a list of tuples
        for orig in orignal_samples:
            new_samples.append([])
            for sample in tqdm(orig): # a reinflection sample
                src_feat, src_form, trg_feat, trg_form = sample
                lemma = self.features_dictionary[src_feat][src_form]
                if lemma != self.features_dictionary[trg_feat][trg_form]: # this can only happen in cases of collision of active-passive Masdars!
                    print(f"Problematic sample: {sample} but found the lemma {lemma}.")
                    bad_samples.append(sample)
                    continue # Don't do anything. I will add them manually.
                # Now, sample from the lemma entries of the train data (d-1) samples.
                # Then, add them to the fourlet, make sure the entire sample doesn't exist anywhere and append it to train_new_samples
                # Do the same to dev and test, and that's it!
                options = list(self.train_lemmas_dictionary[lemma].items())
                if (src_feat,src_form) in options: # this happens mostly in the train file. Whenever it doesn't, ignore that.
                    options.remove((src_feat,src_form)) # make sure the same form isn't chosen again
                if d==2:
                    aux_feat, aux_form = random.sample(options, k=d-1)[0]
                else:
                    raise Exception("Unimplemented section!")
                new_sample = ((src_feat, src_form, aux_feat, aux_form, trg_feat), trg_form)
                new_samples[-1].append(new_sample)
        return new_samples, bad_samples

    def _generate_cross_1(self, d=1):
        """
        Either in form-split or lemma-split mode, the chosen auxiliary lemmas are taken from the train set. The possible lemmas are chosen by the current features.
        The goal is to filter the train lemmas according to the specific src & trg features (that are taken from the dev/test sets -- but it doesn't matter).
        :return: 3 lists of reinflection samples
        """
        assert d in {1,2}, "Only src1_cross1 and src1_cross2 Analogy augmentations are supported!"

        train_samples = deepcopy(self.train_samples)
        dev_samples = deepcopy(self.dev_samples)
        test_samples = deepcopy(self.test_samples)
        orignal_samples_lists = [train_samples, dev_samples, test_samples]
        new_samples, bad_samples = [], [] # going to be a list of tuples
        train_lemmas = deepcopy(self.train_lemmas_dictionary)

        for orignal_samples_list in orignal_samples_lists:
            new_samples.append([])
            for reinflection_sample in tqdm(orignal_samples_list):
                src_feat, src_form, trg_feat, trg_form = reinflection_sample

                # Choose a different lemma, under the condition of having the entries src_feat and trg_feat. Then, take the forms of these features.
                possible_lemmas_dict = filter_dict_by_features(train_lemmas, [src_feat, trg_feat])  # take the partial tables that contain these 2 features.
                # Make sure the same lemma isn't chosen again
                possible_lemmas = list(possible_lemmas_dict.keys())

                # region extra-section
                if 'MSDR' in src_feat and 'MSDR' not in trg_feat: # Masdars might appear in 2 paradigms
                    lemma = self.features_dictionary[trg_feat][trg_form]
                else:
                    lemma = self.features_dictionary[src_feat][src_form]
                # endregion extra-section

                if lemma in possible_lemmas:
                    possible_lemmas.remove(lemma) # don't use the original lemma ; also, features_dictionary[src_feat][src_form]==features_dictionary[trg_feat][trg_form]

                chosen_lemmas = random.sample(possible_lemmas, k=d)

                # Arrange all the elements into the new sample according to an agreed schema.
                if d == 1:
                    chosen_lemma = chosen_lemmas[0]
                    aux_src_form = possible_lemmas_dict[chosen_lemma][src_feat]
                    aux_trg_form = possible_lemmas_dict[chosen_lemma][trg_feat]
                    new_sample = ((src_feat, src_form, aux_src_form, aux_trg_form, trg_feat), trg_form)
                else: # d == 2
                    chosen_lemma1 = chosen_lemmas[0]
                    aux1_src_form = possible_lemmas_dict[chosen_lemma1][src_feat]
                    aux1_trg_form = possible_lemmas_dict[chosen_lemma1][trg_feat]
                    chosen_lemma2 = chosen_lemmas[1]
                    aux2_src_form = possible_lemmas_dict[chosen_lemma2][src_feat]
                    aux2_trg_form = possible_lemmas_dict[chosen_lemma2][trg_feat]
                    new_sample = ((src_feat, src_form, aux1_src_form, aux1_trg_form, aux2_src_form, aux2_trg_form, trg_feat), trg_form)
                new_samples[-1].append(new_sample)

        return new_samples, bad_samples


    def _generate_cross2(self):
        return self._generate_cross_1(d=2)

    def generate_data(self, choice, *args):
        assert choice in {'src2', 'src1_cross1', 'src1_cross2'}, "Invalid Analogy mode!"
        return self._choices[choice]["generate"](*args)

    # region writing-methods
    @staticmethod
    def _source_2_reinflection(line: ([str], str)) ->  ([[str]], [str]):
        (src_feat, src_form, aux_feat, aux_form, trg_feat), trg_form = line
        # return [src_feat.split(";"), list(src_form), aux_feat.split(";"), list(aux_form), trg_feat.split(";")], list(trg_form)
        return [spl_fe(src_feat), spl_fo(src_form), spl_fe(aux_feat), spl_fo(aux_form), spl_fe(trg_feat)], spl_fo(trg_form)

    @staticmethod
    def _cross1_reinflection(line: ([str], str)) ->  ([[str]], [str]):
        (src_feat, src_form, aux_src_form, aux_trg_form, trg_feat), trg_form = line
        return [spl_fe(src_feat), spl_fo(src_form), spl_fo(aux_src_form), spl_fo(aux_trg_form), spl_fe(trg_feat)], spl_fo(trg_form)

    @staticmethod
    def _cross2_reinflection(line: ([str], str)) ->  ([[str]], [str]):
        (src_feat, src_form, aux1_src_form, aux1_trg_form, aux2_src_form, aux2_trg_form, trg_feat), trg_form = line
        return [spl_fe(src_feat), spl_fo(src_form), spl_fo(aux1_src_form), spl_fo(aux1_trg_form), spl_fo(aux2_src_form), spl_fo(aux2_trg_form), spl_fe(trg_feat)], spl_fo(trg_form)
    # endregion writing-methods

    # region reading-methods
    @staticmethod
    def _source_2_sample2data(src:[str], trg: [str]) -> ([[str]], str):
        fe1, fo1, fe2, fo2, fe3 = ','.join(src).split(',+,')
        fe1, fo1, fe2, fo2, fe3 = join_fe(fe1), join_fo(fo1), join_fe(fe2), join_fo(fo2), join_fe(fe3)
        src = fe1, fo1, fe2, fo2, fe3
        trg = ''.join(trg)
        return src, trg

    @staticmethod
    def _cross1_sample2data(src:str, trg: str) -> ([[str]], str):
        fe1, fo1, fo2, fo3, fe2 = src.split(',+,')
        fe1, fo1, fo2, fo3, fe2 = join_fe(fe1), join_fo(fo1), join_fo(fo2), join_fo(fo3), join_fe(fe2)
        src = fe1, fo1, fo2, fo3, fe2
        trg = ''.join(trg.split(','))
        return src, trg

    @staticmethod
    def _cross2_sample2data(src:[str], trg: [str]) -> ([[str]], str):
        fe1, fo1, fo2, fo3, fo4, fo5, fe2 = ','.join(src).split(',+,')
        fe1, fo1, fo2, fo3, fo4, fo5, fe2 = join_fe(fe1), join_fo(fo1), join_fo(fo2), join_fo(fo3), join_fo(fo4), join_fo(fo5), join_fe(fe2)
        src = fe1, fo1, fo2, fo3, fo4, fo5, fe2
        trg = ''.join(trg)
        return src, trg
    # endregion reading-methods

    def analogy_reinflection2TSV(self, method:str, fn, data) -> str:
        # Encapsulating the automatic invoking of the parent method, but with different suffix and parsing method.
        return self.reinflection2TSV(fn, suffix=self._choices[method]["str"], new_dir=self.new_dir, parsing_func=self._choices[method]["data2sample"], data=data)

    def analogy_sample2data(self, inp, choice:str, has_sources=False):
        # limited tells whether the source sequences are supplied.
        if has_sources: # no sources
            src, trg, pred = inp
            pred = ''.join(pred)
            src, trg = self.sample2reinflection((src, trg), parsing_func=self._choices[choice]["sample2data"])
            return src, trg, pred
        else:
            trg, pred = inp
            return ''.join(trg), ''.join(pred)


def main():
    original_dir = os.path.join(".data", "OriginalData")
    analogies_dir = os.path.join(".data", "AnalogiesData", analogy_type)
    inflections_file = os.path.join(".data", "OriginalData", "Inflection Tables Georgian.txt")
    original_train_file, original_dev_file, original_test_file = [f"{training_mode}sp.schema2.{e}.txt" for e in ['train', 'dev', 'test']]

    # if not os.path.isdir(analogies_dir):
    #     os.makedirs(analogies_dir)

    kat_analogies = AnalogyFunctionality(original_dir, analogies_dir, inflections_file, original_train_file, original_dev_file, original_test_file)
    analogised_data, bad_samples = kat_analogies.generate_data(choice=analogy_type)

    # region fix_corrupt_samples
    if analogy_type=='src2':
        assert [len(e) for e in analogised_data] == [7995, 998, 1000] # 7 more manually-generated samples are required.
        auxs = [['V;s1;sSG;IND;PRF', 'დავმალულვარ'], ['V;s3;sSG;IND;PRF', 'დახრჩობილა'], ['V;s3;sSG;OPT', 'დაიხრჩოს'],
                ['V;s3;sSG;IND;PST;PFV', 'აშენდა'], ['V;s3;sPL;IND;PRF', 'აშენებულან'], # to the train-set
                ['V;s1;sPL;IND;PST;PFV', 'შევიჭამეთ'], ['V;s3;sPL;COND', 'აშენდებოდნენ']] # to the dev-set
        corrected_samples = []
        for i,s in enumerate(bad_samples):
            a = list(s)
            new_s = (tuple([*a[:2], *auxs[i], a[2]]), a[3])
            corrected_samples.append(new_s)
        analogised_data[0].extend(corrected_samples[:5])
        analogised_data[1].extend(corrected_samples[5:])
        assert [len(e) for e in analogised_data] == [8000, 1000, 1000] # as the original datasets
        print("The problematic samples were manually corrected.\n")
    # endregion fix_corrupt_samples

    trn_analogy_data, dev_analogy_data, tst_analogy_data = analogised_data
    print(f"Generating {training_mode}-split {analogy_type} analogy datasets:")
    train_file = kat_analogies.analogy_reinflection2TSV(analogy_type, original_train_file, data=trn_analogy_data)
    print(f"Generated data for {train_file}")
    dev_file = kat_analogies.analogy_reinflection2TSV(analogy_type, original_dev_file, data=dev_analogy_data)
    print(f"Generated data for {dev_file}")
    test_file = kat_analogies.analogy_reinflection2TSV(analogy_type, original_test_file, data=tst_analogy_data)
    print(f"Generated data for {test_file}")

def auxiliary_main():
    # A short script for making sure the chosen auxiliary lemmas are differet from the original ones.
    training_mode = 'form'
    analogy_type = 'src1_cross1'
    original_dir = os.path.join(".data", "OriginalData")
    analogies_dir = os.path.join(".data", "AnalogiesData", analogy_type)
    inflections_file = os.path.join(".data", "OriginalData", "Inflection Tables Georgian.txt")
    orig_trn_file, orig_dev_file, orig_tst_file = [f"{training_mode}sp.schema2.{e}.txt" for e in ['train', 'dev', 'test']]

    kat_analogies = AnalogyFunctionality(inflections_file, analogies_dir, orig_trn_file, orig_dev_file, orig_tst_file)

    train_analog_path = os.path.join(analogies_dir, f"{training_mode}sp.schema2.train_{analogy_type}.tsv")
    train_lines = open(train_analog_path, encoding='utf8').read().split('\n')
    train_lines = [line.strip().split('\t') for line in train_lines]
    train_data = []
    i=0
    for line in train_lines:
        src, trg = kat_analogies.analogy_sample2data(line,analogy_type)
        if analogy_type=='src1_cross1':
            fe1, fo1, fo_aux1, fo_aux2, fe2 = src
            bads = [] # 1st and 2nd error types stand for ambiguities at the lemmas correspond to a given Masdar forms.
            if not kat_analogies.features_dictionary[fe1][fo1] == kat_analogies.features_dictionary[fe2][trg]:
                bads.append((1, fo1, trg)) # Don't worry if it's printed
            if not kat_analogies.features_dictionary[fe1][fo_aux1] == kat_analogies.features_dictionary[fe2][fo_aux2]:
                bads.append((2, fo_aux1, fo_aux2)) # Don't worry if it's printed
            if kat_analogies.features_dictionary[fe1][fo1]==kat_analogies.features_dictionary[fe1][fo_aux1]:
                bads.append((3, fo1, fo_aux1)) # Do worry if it's printed
            if bads:
                print(f"{i+1}. The sample: {src, trg}. Bad ones: {bads}")
                i+=1
        train_data.append((src,trg))
    print("Done")

original_dir = os.path.join(".data", "OriginalData")
analogies_dir = os.path.join(".data", "AnalogiesData", analogy_type)
inflections_file = os.path.join(".data", "OriginalData", "Inflection Tables Georgian.txt")
orig_trn_file, orig_dev_file, orig_tst_file = [f"{training_mode}sp.schema2.{e}.txt" for e in ['train', 'dev', 'test']]
analogies_converter = AnalogyFunctionality(inflections_file, analogies_dir, orig_trn_file, orig_dev_file, orig_tst_file)

if __name__ == '__main__':
    main()
    # auxiliary_main()
