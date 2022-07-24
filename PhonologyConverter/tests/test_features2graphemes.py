import unittest
from PhonologyConverter.languages_setup import LanguageSetup
from data import exact_match_examples

class Features2GraphemesTestCase(unittest.TestCase):
    def test_prefix_padding(self):
        for language, word in exact_match_examples.items():
            phonology_converter = LanguageSetup.create_phonology_converter(language)
            features = phonology_converter.word2phonemes(word, mode='features')
            
            self.assertEqual(features, phonology_converter.word2phonemes(word, 'features'))
            self.assertEqual(word, phonology_converter.phonemes2word(features, 'features'))
    
            padded_features = ['$'] * 50 + features
            recons_normalized_word = phonology_converter.phonemes2word(padded_features, 'features', normalize=True)
            self.assertEqual(word, recons_normalized_word)

    def test_suffix_padding(self):
        for language, word in exact_match_examples.items():
            phonology_converter = LanguageSetup.create_phonology_converter(language)
            features = phonology_converter.word2phonemes(word, mode='features')

            self.assertEqual(features, phonology_converter.word2phonemes(word, 'features'))
            self.assertEqual(word, phonology_converter.phonemes2word(features, 'features'))

            padded_features = features + ['$'] * 50
            recons_normalized_word = phonology_converter.phonemes2word(padded_features, 'features', normalize=True)
            self.assertEqual(word, recons_normalized_word)

    # def test_infix_dollars_padding(self):
    #     for language, word in exact_match_examples.items():
    #         phonology_converter = LanguageSetup.create_phonology_converter(language)
    #         features = phonology_converter.word2phonemes(word, mode='features')
    #
    #         self.assertEqual(features, phonology_converter.word2phonemes(word, 'features'))
    #         self.assertEqual(word, phonology_converter.phonemes2word(features, 'features'))
    #
    #         # for each index in an example where example[index] == '$',
    #         # replace it with _X dollars. _X i iterates from 1 to 20.
    #         for pad_size in range(1, 30):
    #             # dollar_indices = np.where(np.array(features) == '$')[0]
    #             # now insert in these indices the sub-lists ['$'] * pad_size
    #
    #             padded_features = features + ['$'] * 50
    #             recons_normalized_word = phonology_converter.phonemes2word(padded_features, 'features', normalize=True)
    #             self.assertEqual(word, recons_normalized_word)


if __name__ == '__main__':
    unittest.main()
