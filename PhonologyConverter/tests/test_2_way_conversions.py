import unittest
from PhonologyConverter.languages_setup import LanguageSetup
from editdistance import eval as edit_distance_eval
from data import exact_match_examples, non_exact_match_examples, expected_edit_distances

# Note: in order to run the test suite, you might need to redirect the phonemes.json path in g2p_config.py
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
