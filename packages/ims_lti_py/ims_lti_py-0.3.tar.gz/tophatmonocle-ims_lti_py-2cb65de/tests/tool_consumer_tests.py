from tool_consumer import ToolConsumer
from test_helper import create_test_tc
import unittest

class TestToolConsumer(unittest.TestCase):
    def test_signature(self):
        '''
        Should generate correct oauth signature.
        '''
        tc = create_test_tc()
        result = tc.generate_launch_data()
        self.assertNotEqual(result, None)
        self.assertEqual(result['oauth_signature'],
                'TPFPK4u3NwmtLt0nDMP1G1zG30U=')

    def test_url_query_parameters(self):
        '''
        Should generate a correct signature with URL query parameters.
        '''
        tc = create_test_tc()
        tc.launch_url = 'http://dr-chuck.com/ims/php-simple/tool.php?a=1&b=2&c=3%20%26a'
        result = tc.generate_launch_data()
        self.assertNotEqual(result, None)
        self.assertEquals(result['oauth_signature'], 
                'uF7LooyefQN5aocx7UlYQ4tQM5k=')
        self.assertEquals(result['c'], '3 &a')

    def test_signature_port(self):
        '''
        Should generate a correct signature with a non-standard port.
        '''
        tc = ToolConsumer('12345', 'secret', {'resource_list_id': 1})
        tc.timestamp = '1251600739'
        tc.nonce = 'c8350c0e47782d16d2fa48b2090c1d8f'

        def test_url(url, sig):
            tc.launch_url = url
            ld = tc.generate_launch_data()
            self.assertNotEqual(ld, None)
            self.assertEquals(ld['oauth_signature'], sig)

        test_url('http://dr-chuck.com:123/ims/php-simple/tool.php', 'HdHJri8Z7OhnMhxX27hSPB5W+SI=')
        test_url('http://dr-chuck.com/ims/php-simple/tool.php', 'bTcODyqQSdogpn1mJAugGB2c2F4=')
        test_url('http://dr-chuck.com:80/ims/php-simple/tool.php', 'bTcODyqQSdogpn1mJAugGB2c2F4=')
        test_url('http://dr-chuck.com:443/ims/php-simple/tool.php', 'n0P6aFgyv6ikNsMiNNG/KjxMZ8w=')
        test_url('https://dr-chuck.com/ims/php-simple/tool.php', '9DoVeq1RYnidTgF71Zg16SNJFpY=')
        test_url('https://dr-chuck.com:443/ims/php-simple/tool.php', '9DoVeq1RYnidTgF71Zg16SNJFpY=')
        test_url('https://dr-chuck.com:80/ims/php-simple/tool.php', '4L1f5SctEX0num3GPElvMKq2w+s=')
        test_url('https://dr-chuck.com:80/ims/php-simple/tool.php?oi=hoyt', 'dvvQchwqhDH1nFGzWbgVxmcUysc=')

    def test_uri_query_parameters(self):
        '''
        Should include URI query parameters.
        '''
        tc = ToolConsumer('12345', 'secret', {
            'resource_link_id': 1,
            'user_id': 2
            })
        tc.launch_url = 'http://www.yahoo.com?a=1&b=2'
        result = tc.generate_launch_data()
        self.assertNotEqual(result, None)
        self.assertEqual(result['a'], '1')
        self.assertEqual(result['b'], '2')

    def test_overite_uri_query_parameters(self):
        '''
        Should not allow overwriting other parameters from the URI query
        string.
        '''
        tc = ToolConsumer('12345', 'secret', {
            'resource_link_id': 1,
            'user_id': 2
            })
        tc.launch_url = 'http://www.yahoo.com?user_id=123&lti_message_type=1234'
        result = tc.generate_launch_data()
        self.assertNotEqual(result, None)
        self.assertEqual(result['user_id'], '2')
        self.assertEqual(result['lti_message_type'],
                'basic-lti-launch-request')
