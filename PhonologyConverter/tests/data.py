# This file contains the toy data used for the UTs.

exact_match_examples = {'kat': 'არ მჭირდ-ებოდყეტ', 'swc': "magnchdhe-ong jwng'a",
                        'sqi': 'rdhëije rrçlldgj-ijdhegnjzh',
                        'lav': 'abscā t-raķkdzhēļšanģa', 'bul': 'най-ясюногщжто'}

# For the problematic languages, the expected difference is also attached
non_exact_match_examples = { 'hun': 'hűdályiokró- l eéfdzgycsklynndzso nyoyaxy',
                             'tur': 'yığmalılksar mveğateğwypûrtâşsmış',
                             'fin': 'ixlmksnngvnk- èeé aatööböyynyissä'}
expected_edit_distances = {'hun': {'p': 2, 'f': 2}, 'tur': {'p': 5, 'f': 6}, 'fin': {'p': 4, 'f': 4}}

