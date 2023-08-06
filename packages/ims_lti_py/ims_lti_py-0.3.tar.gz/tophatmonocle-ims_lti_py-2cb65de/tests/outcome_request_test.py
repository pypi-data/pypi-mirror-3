from test_helper import create_test_tp
from outcome_request import OutcomeRequest

import unittest

class TestOutcomeRequest(unittest.TestCase):
    def setUp(self):
        self.tp = create_test_tp()
        self.expected_xml = '<?xml version="1.0" encoding="UTF-8"?><imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/lis/oms1p0/pox"><imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier>123456789</imsx_messageIdentifier></imsx_POXRequestHeaderInfo></imsx_POXHeader><imsx_POXBody>%s</imsx_POXBody></imsx_POXEnvelopeRequest>'
        self.replace_result_xml = self.expected_xml[:] %('<replaceResultRequest><resultRecord><sourcedGUID><sourcedId>261-154-728-17-784</sourcedId></sourcedGUID><result><resultScore><language>en</language><textString>5</textString></resultScore></result></resultRecord></replaceResultRequest>')
        self.read_result_xml = self.expected_xml[:] %('<readResultRequest><resultRecord><sourcedGUID><sourcedId>261-154-728-17-784</sourcedId></sourcedGUID></resultRecord></readResultRequest>')
        self.delete_result_xml = self.expected_xml[:] %('<deleteResultRequest><resultRecord><sourcedGUID><sourcedId>261-154-728-17-784</sourcedId></sourcedGUID></resultRecord></deleteResultRequest>')
         
    #def test_post_replace_result(self):
    #    '''
    #    Should post replaceResult rquest.
    #    '''
    #    self.tp.post_replace_result(5)
    #    self.assetFalse(self.tp.last_outcome_success)

    #def test_post_read_result(self):
    #    '''
    #    Should post readResult request.
    #    '''
    #    self.tp.post_read_result()

    #def  test_post_delete_result(self):
    #    '''
    #    Should post deleteResult request.
    #    '''
    #    self.tp.post_delete_result()

    def test_parse_replace_result_xml(self):
        '''
        Should parse replaceResult XML.
        '''
        request = OutcomeRequest()
        request.process_xml(self.replace_result_xml)
        self.assertEqual(request.options['operation'], 'replaceResult')
        self.assertEqual(request.options['lis_result_sourcedid'], '261-154-728-17-784')
        self.assertEqual(request.options['message_identifier'], '123456789')
        self.assertEqual(request.options['score'], '5')

    def test_parse_read_result_xml(self):
        '''
        Should parse readResult XML.
        '''
        request = OutcomeRequest()
        request.process_xml(self.read_result_xml)
        self.assertEqual(request.options['operation'], 'readResult')
        self.assertEqual(request.options['lis_result_sourcedid'], '261-154-728-17-784')
        self.assertEqual(request.options['message_identifier'], '123456789')
        self.assertEqual(request.options['score'], None)

    def test_parse_delete_result_xml(self):
        '''
        Should parse deleteRequest XML.
        '''
        request = OutcomeRequest()
        request.process_xml(self.delete_result_xml)
        self.assertEqual(request.options['operation'], 'deleteResult')
        self.assertEqual(request.options['lis_result_sourcedid'], '261-154-728-17-784')
        self.assertEqual(request.options['message_identifier'], '123456789')
        self.assertEqual(request.options['score'], None)
