import unittest
import requests
from pyfaceb import FBGraph
from mock import patch, Mock
from pyfaceb.exceptions import (FBJSONException, FBHTTPException,
                                FBConnectionException)
from requests.exceptions import SSLError
from pyfaceb.api import FBQuery

class FBGraphTest(unittest.TestCase):
    
    def test_basic_get_personal_profile(self):
        expected = {
            u'username': u'kevin.r.stanton',
            u'first_name': u'Kevin',
            u'last_name': u'Stanton',
            u'name': u'Kevin Stanton',
            u'locale': u'en_US',
            u'gender': u'male',
            u'id': u'537208670'
        }
        fbg = FBGraph()
        result = fbg.get('kevin.r.stanton')
        self.assertDictEqual(expected, result)
        
    def test_basic_get_company_profile(self):
        fbg = FBGraph()
        result = fbg.get('SproutSocialInc')
        self.assertIsInstance(result, dict)
        self.assertEquals('2009', result['founded'])
        self.assertEquals('Sprout Social', result['name'])
        self.assertEquals('138467959508514', result['id'])
        self.assertEquals('SproutSocialInc', result['username'])

    @patch.object(requests, 'request')
    def test_FBJSONException(self, request):
        mock_response = Mock()
        mock_response.text = 'i am bad json'
        mock_response.status_code = 200
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBJSONException, fbg.get, 'me')

    @patch.object(requests, 'request')
    def test_FBHTTPException(self, request):
        mock_response = Mock()
        mock_response.text = 'some fb error'
        mock_response.status_code = 400
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBHTTPException, fbg.get, 'me')
        try:
            data = fbg.get('me')
        except FBHTTPException as e:
            self.assertEquals(e.message, 'some fb error')

    @patch.object(requests, 'request')
    def test_FBConnectionException(self, request):
        def side_effect(*args, **kwargs):
            raise SSLError('The read operation timed out')
        request.side_effect = side_effect

        fbg = FBGraph()
        self.assertRaises(FBConnectionException, fbg.get, 'me')
        self.assertRaises(FBConnectionException, fbg.post,
            'me', payload={'junk': 'data'})

class FBQueryTest(unittest.TestCase):
    @patch.object(requests, 'request')
    def test_basic_query(self, request):
        mock_response = Mock()
        mock_response.text = '{"data": [{"metric": "post_impressions_unique", '
        mock_response.text += '"value": 6740, "object_id": "123_456"}]}'
        mock_response.status_code = 200
        request.return_value = mock_response

        qry = 'select object_id, value, metric from insights where object_id '
        qry += 'in (\'123_456\') and metric in (\'post_impressions_unique\') '
        qry += 'and period=period(\'lifetime\')'

        fbq = FBQuery('fakeaccesstoken')
        data = fbq.query(qry)

        self.assertEquals(len(data['data']), 1)
        self.assertDictEqual(data['data'][0], {
            'object_id': '123_456',
            'metric': 'post_impressions_unique',
            'value': 6740
        })

