import unittest
import requests
from pyfaceb import FBGraph

class PrivateFBGraphTest(unittest.TestCase):
    
    def setUp(self):
        self.app_token = '331741700416|01ec39fb610384903eb07d45.1-100001644838653|KQkWFp3oVGO51yc134qkdWZ5zhk'
        self.sp_tk = "AAAAATT1YoUABAH9MZAjm6zmA7E0CCq9CwRl9geGAhfaqoWgCKEEjH9J27ThqdW1VcdDknnZAXTrIHgFn7VM6etYYjoiZBYZD"
        self.ww_tk = "AAAAATT1YoUABAFzlw8aAmZCYThcBqpWtKqO8X65IaFE3mdp0CSvJWBmuGye2MJaBQlbABVJwZA0ZC0ocRFMEkvi0ZBhZC4m0ZD"
        self.sp_qry = "select object_id, metric, value from insights where object_id in ('138467959508514_344497162238925') and metric in ('post_consumptions_by_type_unique') AND period=period('lifetime')"
        self.ww_qry = "select object_id, metric, value from insights where object_id in ('8532248414_337758452940093', '8532248414_152638451531756', '8532248414_10150709496538415', '8532248414_10150765498488415', '8532248414_361423777241884', '8532248414_10150741833668415', '8532248414_10150726972268415', '8532248414_269707296452066', '8532248414_217399405032310', '8532248414_197659927015116', '8532248414_10150772347493415', '8532248414_111886322277694', '8532248414_10150763759538415', '8532248414_10150739692443415', '8532248414_275172479232347', '8532248414_10150754088843415', '8532248414_328293580557373', '8532248414_412961728732701', '8532248414_420623574631193', '8532248414_392147040804195', '8532248414_353266711390912', '8532248414_10150725141588415', '8532248414_325652164160584', '8532248414_10150703105173415', '8532248414_302439166494056') and metric in ('post_impressions_unique', 'post_consumptions_unique', 'post_storytellers', 'post_storytellers_by_action_type', 'post_negative_feedback_unique') AND period=period('lifetime')"
        
    def test_basic_batched_graph_call(self):
        rqst1 = {'method': 'GET', 'relative_url': '537208670'}
        rqst2 = {'method': 'GET', 'relative_url': '138467959508514'}
        batches = [rqst1, rqst2]
        
        fbg = FBGraph(self.app_token)
        result = fbg.batch(batches)
        self.assertIsInstance(result, list)
        for resp in result:
            self.assertTrue('body' in resp)
            self.assertTrue('code' in resp)
            self.assertTrue('headers' in resp)
            
        self.assertEquals('Kevin', result[0]['body']['first_name'])
        self.assertEquals('Sprout Social', result[1]['body']['name'])
        print result
        
    #TODO:
    def test_mixed_http_verb_batched_graph_call(self):
        pass
    
    def test_single_fql(self):
        fbg = FBGraph(self.sp_tk)
        result = fbg.get('fql', params={'q': self.sp_qry})
        self.assertIsInstance(result, dict)
        self.assertTrue('data' in result)
        self.assertTrue('metric' in result['data'][0])
        self.assertTrue('value' in result['data'][0])
        self.assertTrue('object_id' in result['data'][0])
        self.assertEquals(result['data'][0]['object_id'], u'138467959508514_344497162238925')
        
    def test_batched_fql(self):
        sp_rqst = {
            'method': 'POST',
            'relative_url': 'method/fql.query?query=' + self.sp_qry,
            'body': 'access_token=' + self.sp_tk
        }
        ww_rqst = {
            'method': 'POST',
            'relative_url': 'method/fql.query?query=' + self.ww_qry,
            'body': 'access_token=' + self.ww_tk
        }
        
        batches = [sp_rqst, ww_rqst]
        fbg = FBGraph(self.app_token)
        data = fbg.batch(batches)
        
        self.assertIsInstance(data, list)
        self.assertEquals(len(data), 2)
        for resp in data:
            self.assertTrue('body' in resp)
            self.assertTrue('code' in resp)
            self.assertTrue('headers' in resp)
            self.assertIsInstance(resp['body'], list)
        print data
        
    def test_basic_picture_post(self):
        token = 'AAAAATT1YoUABAMZAYSV8iMKdk7NuaRlAjc0pVFIdg7FdHZA5rfXySQiP5la91lWJQUJZCVn9APwvR1WykIU0Mou6cw3tZAsZD'
        fbg = FBGraph(token)
        pic = open('s2_logo.png', 'rb')
        result = fbg.post('me', 'photos', payload={'message': "Photo post test.", 'source': pic})
        self.assertIsInstance(result, dict)
        self.assertTrue('post_id' in result)
        self.assertTrue('id' in result)
        print result
        
        # clean up
        # Need to clean up manually, we don't have the right permissions to delete a photo
#        r = requests.delete('https://graph.facebook.com/' + str(result['id']), params={'access_token': token})
#        print r.text
#        self.assertEquals(r.status_code, 200)
        
    def test_basic_status_post(self):
        token = 'AAAAATT1YoUABAMZAYSV8iMKdk7NuaRlAjc0pVFIdg7FdHZA5rfXySQiP5la91lWJQUJZCVn9APwvR1WykIU0Mou6cw3tZAsZD'
        fbg = FBGraph(token)
        result = fbg.post('me', 'feed', payload={'message': 'test statuspost'})
        self.assertIsInstance(result, dict)
        self.assertTrue('id' in result)
        
        # clean up
        r = requests.delete('https://graph.facebook.com/' + str(result['id']), params={'access_token': token})
        print r.text
        self.assertEquals(r.status_code, 200)
        
    def test_get_friends(self):
        token = 'AAAAATT1YoUABAMZAYSV8iMKdk7NuaRlAjc0pVFIdg7FdHZA5rfXySQiP5la91lWJQUJZCVn9APwvR1WykIU0Mou6cw3tZAsZD'
        fbg = FBGraph(token)
        result = fbg.get('me', 'friends', params={'limit': 10})
        print result
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['data'], list)
        self.assertEquals(len(result['data']), 10)
        