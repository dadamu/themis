import unittest

import httpretty

import twitter


class TestTwitter(unittest.TestCase):

    @httpretty.activate(verbose=True, allow_net_connect=False)
    def test_get_data_from_tweet(self):
        # Register fake HTTP call
        httpretty.register_uri(
            httpretty.GET,
            "https://themis.morpheus.desmos.network/twitter/tweets/1392033585675317252",
            status=200,
            body='{"author":{"username":"ricmontagnin"},"text":"https://t.co/uD23HgSLJW"}',
        )

        username, urls = twitter.get_data_from_tweet('1392033585675317252')
        self.assertEqual('ricmontagnin', username)
        self.assertEqual(['https://t.co/uD23HgSLJW'], urls)

    @httpretty.activate(verbose=True, allow_net_connect=False)
    def test_get_data_from_bio(self):
        # Register fake HTTP call
        httpretty.register_uri(
            httpretty.GET,
            "https://themis.morpheus.desmos.network/twitter/users/ricmontagnin",
            status=200,
            body='{"username":"ricmontagnin","bio":"https://t.co/uD23HgSLJW"}',
        )

        username, urls = twitter.get_data_from_bio('ricmontagnin')
        self.assertEqual('ricmontagnin', username)
        self.assertEqual(['https://t.co/uD23HgSLJW'], urls)

    @httpretty.activate(verbose=True, allow_net_connect=False)
    def test_get_signature_from_url(self):
        # Register fake HTTP call
        httpretty.register_uri(
            httpretty.GET,
            "https://pastebin.com/raw/xz4S8WrW",
            status=200,
            body='{"address":"desmos13yp2fq3tslq6mmtq4628q38xzj75ethzela9uu","pub_key":"033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d","signature":"a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173","value":"ricmontagnin"}',
        )

        # Valid signature
        data = twitter.get_signature_from_url('https://pastebin.com/raw/xz4S8WrW')
        self.assertIsNotNone(data)

        # Register fake HTTP call
        httpretty.register_uri(
            httpretty.GET,
            "https://bitcoin.org",
            status=200,
            body='Bitcoin website',
        )

        # Invalid signature
        data = twitter.get_signature_from_url('https://bitcoin.org')
        self.assertIsNone(data)

    def test_validate_json(self):
        jsons = [
            {
                'name': 'Valid JSON',
                'json': {
                    'address': '8902A4822B87C1ADED60AE947044E614BD4CAEE2',
                    'pub_key': '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'signature': 'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                    'value': 'ricmontagnin'
                },
                'valid': True
            },
            {
                'name': 'Missing address',
                'json': {
                    'pub_key': '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'signature': 'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                    'value': 'ricmontagnin'
                },
                'valid': False
            },
            {
                'name': 'Missing pub_key',
                'json': {
                    'address': '8902A4822B87C1ADED60AE947044E614BD4CAEE2',
                    'signature': 'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                    'value': 'ricmontagnin'
                },
                'valid': False
            },
            {
                'name': 'Missing signature',
                'json': {
                    'address': '8902A4822B87C1ADED60AE947044E614BD4CAEE2',
                    'pub_key': '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'value': 'ricmontagnin'
                },
                'valid': False
            },
            {
                'name': 'Missing value',
                'json': {
                    'address': '8902A4822B87C1ADED60AE947044E614BD4CAEE2',
                    'pub_key': '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'signature': 'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                },
                'valid': False
            },
        ]

        for json in jsons:
            result = twitter.validate_json(json['json'])
            self.assertEqual(json['valid'], result, json['name'])

    def test_verify_signature(self):
        tests = [
            {
                'name': 'Valid data',
                'valid': True,
                'data': twitter.VerificationData(
                    '',
                    '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    '7269636d6f6e7461676e696e',
                    'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                ),
            },
            {
                'name': 'Invalid value',
                'valid': False,
                'data': twitter.VerificationData(
                    '',
                    '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                    'ricmontagni',
                ),
            },
            {
                'name': 'Invalid signature',
                'valid': False,
                'data': twitter.VerificationData(
                    '',
                    '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'a00a7d5bd45e42615645fcaeb4d800af2704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                    '7269636d6f6e7461676e696e',
                ),
            },
            {
                'name': 'Invalid pub key',
                'valid': False,
                'data': twitter.VerificationData(
                    '',
                    '033024e9e0ad4f9305ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173',
                    '7269636d6f6e7461676e696e',
                ),
            },
        ]

        for test in tests:
            result = twitter.verify_signature(test['data'])
            self.assertEqual(test['valid'], result, test['name'])

    def test_verify_address(self):
        tests = [
            {
                'name': 'Valid address',
                'valid': True,
                'data': twitter.VerificationData(
                    '8902A4822B87C1ADED60AE947044E614BD4CAEE2',
                    '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b417d',
                    '7269636d6f6e7461676e696e',
                    'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173'
                ),
            },
            {
                'name': 'Invalid address',
                'valid': False,
                'data': twitter.VerificationData(
                    '8902A4822B87C1ADED60AE947044E614BD4CAEE2',
                    '033024e9e0ad4f93045ef5a60bb92171e6418cd13b082e7a7bc3ed05312a0b41',
                    '7269636d6f6e7461676e696e',
                    'a00a7d5bd45e42615645fcaeb4d800af22704e54937ab235e5e50bebd38e88b765fdb696c22712c0cab1176756b6346cbc11481c544d1f7828cb233620c06173'
                ),
            },
        ]

        for test in tests:
            result = twitter.verify_address(test['data'])
            self.assertEqual(test['valid'], result, test['name'])


if __name__ == '__main__':
    unittest.main()
