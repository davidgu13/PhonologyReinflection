from os.path import join
from typing import Callable, Dict, Iterable, List, Tuple


def inflection_reinflection_file_iterator(file_name: str, add_split_line_to_object: Callable,
                                          empty_samples_object: Iterable, mode: str):
    """
    Takes a file in inflection or reinflection format, and for each line accumulates the result of line_handler to samples_object.
    :param file_name: the file to be processed
    :param add_split_line_to_object: a method that aggregates the new line
    :param empty_samples_object: the initial object to be accumulated to, e.g. {}, []
    :param mode: if 'inflection' assumes the format {lemma}\t{form}\t{features}; if 'reinflection'
                 assumes {src_feat}\t{src_form}\t{trg_feat}\t{trg_form}
    :return: samples_object
    """
    samples_object = empty_samples_object
    with open(file_name, "r", encoding='utf-8') as f:
        for line in f:
            split_line = line.strip().split("\t")
            if mode == 'inflection':
                lemma, form, features = split_line
                samples_object = add_split_line_to_object(samples_object, lemma, form, features)
            elif mode == 'reinflection':
                src_feat, src_form, trg_feat, trg_form = split_line
                samples_object = add_split_line_to_object(samples_object, src_feat, src_form, trg_feat, trg_form)
            else:
                samples_object = add_split_line_to_object(samples_object, split_line)
    return samples_object


def form_features_tuple(samples_object: Dict, lemma, form, features) -> Dict:
    samples_object[(form, features)] = lemma
    return samples_object


def lemma_features_dict(samples_object: Dict, lemma, form, features) -> Dict:
    if lemma not in samples_object:
        samples_object[lemma] = {}
    samples_object[lemma][features] = form
    return samples_object


def read_paradigms(fname) -> Tuple[Dict[str, Dict[str, str]], Dict[Tuple[str, str], str]]:
    """ Reads the file and creates 2 data structures: {lemma: {feat_i, form_i}} and {(form_i, feat_i): lemma} """
    lemma_feat_form, form_feat_lemma = {}, {}

    with open(fname, 'r', encoding='utf-8') as f:

        for line in f:
            lemma, form, feat = line.strip().split("\t")

            form_feat_lemma[(form, feat)] = lemma

            if lemma not in lemma_feat_form:
                lemma_feat_form[lemma] = {}
            lemma_feat_form[lemma][feat] = form

    return lemma_feat_form, form_feat_lemma


def read_reinflection_file(file_name: str) -> List[Dict[str, Tuple[str, str]]]:
    reinflection_samples = []
    # with

    return [{"src": ("V;", "fdasf")}]


def count_lemmas_in_reinflection_file(paradigms: Dict[Tuple[str, str], str], reinflection_file: str):
    pass


def filter_by_pos():
    pass


def main():
    # get_paradigms_as_tuples(join("..", '.data', 'Reinflection', 'CleanedData', 'tur.V'))
    _, form_feats_dict = read_paradigms(join("..", '.data', 'RawData', 'tur.txt'))
    print(len(form_feats_dict))


if __name__ == '__main__':
    main()
