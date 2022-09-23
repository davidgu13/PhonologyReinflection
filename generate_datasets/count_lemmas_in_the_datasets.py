from os.path import join
from typing import Callable, Collection, Dict, List, Tuple, Union


class LanguagePOSGroup:
    def __init__(self, name: str):
        self.name = name
        split_name = name.split('.')
        self.language = split_name[0]
        self.POS = split_name[1]


def parse_inflections_file(file_name: str, add_split_line_to_object: Callable,
                           empty_samples_object: Collection, line_typle='other') -> Collection:
    """
    Takes a file in inflection or reinflection format and parses every line to a samples object.
    :param file_name: the file to be processed
    :param add_split_line_to_object: a method that parses the line and aggregates it
    :param empty_samples_object: the initial object to be accumulated to, e.g. {}, []
    :param line_typle: if 'inflection' assumes the format {lemma}\t{form}\t{features}; if 'reinflection'
                 assumes {src_feat}\t{src_form}\t{trg_feat}\t{trg_form}
    :return: samples_object
    """
    samples_object = empty_samples_object
    with open(file_name, "r", encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            split_line = line.split("\t")
            if line_typle == 'inflection':
                lemma, form, features = split_line
                samples_object = add_split_line_to_object(samples_object, lemma, form, features)
            elif line_typle == 'reinflection':
                src_feat, src_form, trg_feat, trg_form = split_line
                samples_object = add_split_line_to_object(samples_object, src_feat, src_form, trg_feat, trg_form)
            else:
                samples_object = add_split_line_to_object(samples_object, split_line)
    return samples_object


# region accumulation_methods

def build_lemma_features_dict(samples_object: Dict, lemma, form, features) -> Dict:
    if lemma not in samples_object:
        samples_object[lemma] = {}
    samples_object[lemma][features] = form
    return samples_object


def build_form_features_dict(samples_object: Dict, lemma, form, features) -> Dict:
    samples_object[(form, features)] = lemma
    return samples_object


def build_reinflection_sample_dict(samples_object: List, src_feat, src_form, trg_feat, trg_form) -> List:
    samples_object.append({"src": (src_form, src_feat), "trg": (trg_form, trg_feat)})
    return samples_object


# endregion accumulation_methods

def read_reinflection_file(file_name: str) -> Union[List[Dict[str, Tuple[str, str]]], Collection]:
    return parse_inflections_file(file_name, build_reinflection_sample_dict, [], 'reinflection')


def count_lemmas_in_reinflection_file(paradigms: Dict[Tuple[str, str], str], reinflection_file: str):
    pass


def filter_by_pos(inflections: Dict, pos: str) -> Dict:
    return dict(filter(lambda item: not item[1].startswith(pos), inflections.items()))


def main():
    lang_pos_list = ['kat.V', 'tur.V']
    lang_pos_groups = [LanguagePOSGroup(group) for group in lang_pos_list]

    raw_inflection_file_name = join('..', '..', '.data', 'RawData',
                                    f'{"katVerbsNew" if lang_pos_groups[0].name == "kat.V" else lang_pos_groups[0].language}.txt')
    form_feats_dict = parse_inflections_file(raw_inflection_file_name, build_form_features_dict, {}, 'inflection')
    print(len(form_feats_dict))
    pos_paradigms = filter_by_pos(form_feats_dict, lang_pos_groups[0].POS)
    print(len(pos_paradigms))


    reinflection_file_name = join('..', '..', '.data', 'Reinflection', 'CleanedData', lang_pos_groups[0].name,
                                  f'{lang_pos_groups[0].name}.form.test.txt')
    train_reinflection_samples = read_reinflection_file(reinflection_file_name)
    print(len(train_reinflection_samples))


if __name__ == '__main__':
    main()
