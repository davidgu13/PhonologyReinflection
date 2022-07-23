import unittest
from PhonologyConverter.languages_setup import LanguageSetup
from editdistance import eval as edit_distance_eval
from data import exact_match_examples, non_exact_match_examples, expected_edit_distances

# TODO: Write UTs for 1-way conversions - from features to graphemes (given some lang).
#  Use the examples below + many invalid examples, and also real-world examples
"""
$ $ $ $ 1 2 3 $ 3 NA NA $ NA $ 4 3 NA $ $ $ $ $  ->  [ (1,2,3) (3,NA,NA)  #  (4,3,NA) ]
1 2 3 $ 4 5 6 $ 6 3 NA $ $ 3 NA NA $ $ $ 4 NA NA $  ->  [ (1,2,3) (4,5,6) (6,3,NA) (3,NA,NA)  #  ]
"""
# ('2', '10', '18', '$', '24', '29', 'NA', '$', '33', 'NA', 'NA', '$', '2', '10', '18', '$',
# '24', '29', 'NA', '$', '33', 'NA', 'NA', '$', '26', '28', '30', '$', '2', '16', '19', '$',
# '33', 'NA', 'NA', '$', '2', '10', '18', '$', '24', '29', 'NA', '$', '33', 'NA', 'NA', '$', '$', '33', 'NA', 'NA', '$',
# '2', '11', '19', '$', '8', '12', '19', '$', '26', '28', '30', '$', '22', '27', 'NA', '$', '2', '16', '19')

class PhonologyConverterTestCase(unittest.TestCase):
    def test_2_way_exact_conversions(self):
        # For kat, swc, sqi, lav & bul there should be exact match in the two-way conversions
        for language, word in exact_match_examples.items():
            phonology_converter = LanguageSetup.create_phonology_converter(language)
            phonemes = phonology_converter.word2phonemes(word, mode='phonemes')
            features = phonology_converter.word2phonemes(word, mode='features')

            reconstructed_word_from_phonemes = phonology_converter.phonemes2word(phonemes, mode='phonemes')
            reconstructed_word_from_features = phonology_converter.phonemes2word(features, mode='features')
            self.assertEqual(word, reconstructed_word_from_phonemes)
            self.assertEqual(word, reconstructed_word_from_features)

    def test_edit_distance(self):
        for language, word in non_exact_match_examples.items():
            phonology_converter = LanguageSetup.create_phonology_converter(language)
            phonemes = phonology_converter.word2phonemes(word, mode='phonemes')
            features = phonology_converter.word2phonemes(word, mode='features')

            reconstructed_word_from_phonemes = phonology_converter.phonemes2word(phonemes, mode='phonemes')
            reconstructed_word_from_features = phonology_converter.phonemes2word(features, mode='features')
            self.assertEqual(edit_distance_eval(word, reconstructed_word_from_phonemes), expected_edit_distances[language]['p'])
            self.assertEqual(edit_distance_eval(word, reconstructed_word_from_features), expected_edit_distances[language]['f'])

if __name__ == '__main__':
    unittest.main()
