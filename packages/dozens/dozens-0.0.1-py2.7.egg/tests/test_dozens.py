import json
import dozens
import mock
from unittest import TestCase

try:
    from urllib2 import addinfourl
    from StringIO import StringIO
except:
    from urllib.response import addinfourl
    from io import StringIO


class DozensTestCase(TestCase):

    def test_start(self):
        with mock.patch('dozens.dozens.urlopen') as m:
            m.return_value = self.mock_response({'auth_token': 'dummy_token'})

            testee = dozens.Dozens('user', 'key')
            testee.start()
            self.assertEqual(testee.token, 'dummy_token')

            request = m.call_args[0][0]
            self.assertEqual(request.get_full_url(), testee.AUTHORIZE_URL)
            self.assertEqual(request.get_header('X-auth-user'), 'user')
            self.assertEqual(request.get_header('X-auth-key'), 'key')
            self.assertEqual(request.get_method(), 'GET')

    def test_get_zones(self):
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'
        dummy = [
            {'id': 1, 'name': 'name1'},
            {'id': 2, 'name': 'name2'},
            ]
        response = self.mock_response({'domain': dummy})

        zones, request = self.request(response, testee.get_zones)
        self.assertEqual(zones[0].id, 1)
        self.assertEqual(zones[0].name, 'name1')
        self.assertEqual(zones[1].id, 2)
        self.assertEqual(zones[1].name, 'name2')
        self.assertEqual(request.get_full_url(), testee.GET_ZONES_URL)
        self.assertEqual(request.get_method(), 'GET')

    def test_add_zone(self):
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'
        dummy = [
            {'id': 1, 'name': 'name1'},
            {'id': 2, 'name': 'name2'},
            ]
        response = self.mock_response({'domain': dummy})
        args = ('name2', True, 'google')

        zone, request = self.request(response, testee.add_zone, *args)
        self.assertEqual(zone.id, 2)
        self.assertEqual(zone.name, 'name2')
        self.assertEqual(request.get_full_url(), testee.ADD_ZONE_URL)
        self.assertEqual(request.get_method(), 'POST')

        params = json.loads(request.data)
        self.assertEqual(params['name'], 'name2')
        self.assertEqual(params['google_authorize'], 'google')
        self.assertTrue(params['add_google_apps'])

    def test_delete_zone(self):
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'
        response = self.mock_response({})

        result, request = self.request(response, testee.delete_zone, 1)
        self.assertEqual(request.get_full_url(), testee.DELETE_ZONE_URL % 1)
        self.assertEqual(request.get_method(), 'DELETE')

    def test_get_records(self):
        dummy = [
            {'id': 1,
             'name': 'name1',
             'type': 'type1',
             'prio': 'prio1',
             'content': 'content1',
             'ttl': 7200},
            {'id': 2,
             'name': 'name2',
             'type': 'type2',
             'prio': 'prio2',
             'content': 'content2',
             'ttl': 7200},
            ]
        response = self.mock_response({'record': dummy})
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'

        records, request = self.request(response, testee.get_records, 'domain')
        self.assertEqual(records[0].id, 1)
        self.assertEqual(records[0].name, 'name1')
        self.assertEqual(records[0].type, 'type1')
        self.assertEqual(records[0].priority, 'prio1')
        self.assertEqual(records[0].content, 'content1')
        self.assertEqual(records[0].ttl, 7200)

        self.assertEqual(records[1].id, 2)
        self.assertEqual(records[1].name, 'name2')
        self.assertEqual(records[1].type, 'type2')
        self.assertEqual(records[1].priority, 'prio2')
        self.assertEqual(records[1].content, 'content2')
        self.assertEqual(records[1].ttl, 7200)

        self.assertEqual(request.get_full_url(),
                         testee.GET_RECORDS_URL % 'domain')
        self.assertEqual(request.get_method(), 'GET')

    def test_add_record(self):
        dummy = [
            {'id': 1,
             'name': 'name1',
             'type': 'type1',
             'prio': 'prio1',
             'content': 'content1',
             'ttl': 7200},
            {'id': 2,
             'name': 'name2',
             'type': 'type2',
             'prio': 'prio2',
             'content': 'content2',
             'ttl': 7200},
            ]
        response = self.mock_response({'record': dummy})
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'

        args = ('domain', 'type1', 'content1', 'name1', 'prio1', 7200)
        record, request = self.request(response, testee.add_record, *args)
        self.assertEqual(record.id, 1)
        self.assertEqual(record.name, 'name1')
        self.assertEqual(record.type, 'type1')
        self.assertEqual(record.priority, 'prio1')
        self.assertEqual(record.content, 'content1')
        self.assertEqual(record.ttl, 7200)
        self.assertEqual(request.get_full_url(), testee.ADD_RECORD_URL)
        self.assertEqual(request.get_method(), 'POST')

        params = json.loads(request.data)
        self.assertEqual(params['domain'], 'domain')
        self.assertEqual(params['type'], 'type1')
        self.assertEqual(params['content'], 'content1')
        self.assertEqual(params['name'], 'name1')
        self.assertEqual(params['prio'], 'prio1')
        self.assertEqual(params['ttl'], 7200)

    def test_update_record(self):
        dummy = [
            {'id': 1,
             'name': 'name1',
             'type': 'type1',
             'prio': 'prio1',
             'content': 'content1',
             'ttl': 7200},
            {'id': 2,
             'name': 'name2',
             'type': 'type2',
             'prio': 'prio2',
             'content': 'content2',
             'ttl': 7200},
            ]
        response = self.mock_response({'record': dummy})
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'

        args = (1, 'prio1', 'content1', 7200)
        record, request = self.request(response, testee.update_record, *args)
        self.assertEqual(record.id, 1)
        self.assertEqual(record.name, 'name1')
        self.assertEqual(record.type, 'type1')
        self.assertEqual(record.priority, 'prio1')
        self.assertEqual(record.content, 'content1')
        self.assertEqual(record.ttl, 7200)
        self.assertEqual(request.get_full_url(), testee.UPDATE_RECORD_URL % 1)
        self.assertEqual(request.get_method(), 'POST')

        params = json.loads(request.data)
        self.assertEqual(params['prio'], 'prio1')
        self.assertEqual(params['content'], 'content1')
        self.assertEqual(params['ttl'], 7200)

    def test_delete_record(self):
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'
        response = self.mock_response({})

        result, request = self.request(response, testee.delete_record, 1)
        self.assertEqual(request.get_full_url(), testee.DELETE_RECORD_URL % 1)
        self.assertEqual(request.get_method(), 'DELETE')

    def test_get_empty_zones(self):
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'
        response = self.mock_response([])

        zones, request = self.request(response, testee.get_zones)
        self.assertEqual(zones, [])
        self.assertEqual(request.get_full_url(), testee.GET_ZONES_URL)
        self.assertEqual(request.get_method(), 'GET')

    def test_get_empty_records(self):
        testee = dozens.Dozens('user', 'key')
        testee.token = 'token'
        response = self.mock_response([])

        records, request = self.request(response, testee.get_records, 'domain')
        self.assertEqual(records, [])
        self.assertEqual(request.get_full_url(),
                         testee.GET_RECORDS_URL % 'domain')
        self.assertEqual(request.get_method(), 'GET')

    def test_get_with_query(self):
        with mock.patch('dozens.dozens.urlopen') as m:
            m.return_value = self.mock_response({})

            testee = dozens.Dozens('user', 'key')
            testee.token = 'token'
            testee.get('http://test.com/url', {'key': 'value'})

            request = m.call_args[0][0]
            self.assertEqual(request.get_full_url(), 'http://test.com/url?key=value')
            self.assertEqual(request.get_method(), 'GET')

    def test_models(self):
        zone = dozens.Zone(1, 'name')
        record = dozens.Record(1, 'name', 'type', 'priority', 'content', 7200)
        self.assertEqual(str(zone), 'Zone {id: 1, name: name}')
        self.assertEqual(str(record), ('Record {'
                                       'id: 1, '
                                       'name: name, '
                                       'type: type, '
                                       'priority: priority, '
                                       'content: content, '
                                       'ttl: 7200'
                                       '}'))

    def request(self, response, method, *args):
        with mock.patch('dozens.dozens.urlopen') as m:
            m.return_value = response
            result = method(*args)

            request = m.call_args[0][0]
            content_type = request.get_header('Content-type')
            token = request.get_header('X-auth-token')

            self.assertEqual(content_type, 'application/json')
            self.assertEqual(token, 'token')
            return result, request

    def mock_response(self, value):
        body = StringIO(json.dumps(value))
        response = addinfourl(body, {}, 'dummy_url')
        response.code = 200
        return response
