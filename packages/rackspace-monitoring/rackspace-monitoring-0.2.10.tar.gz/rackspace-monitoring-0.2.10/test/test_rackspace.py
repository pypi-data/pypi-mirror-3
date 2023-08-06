# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import unittest
import json
from os.path import join as pjoin

from libcloud.utils.py3 import httplib, urlparse
from rackspace_monitoring.base import (MonitoringDriver, Entity,
                                      NotificationPlan,
                                      Notification, CheckType, Alarm, Check,
                                      AlarmChangelog)
from rackspace_monitoring.drivers.rackspace import (RackspaceMonitoringDriver,
                                            RackspaceMonitoringValidationError)

from test import MockResponse, MockHttpTestCase
from test.file_fixtures import FIXTURES_ROOT
from test.file_fixtures import FileFixtures
from secrets import RACKSPACE_PARAMS

FIXTURES_ROOT['monitoring'] = pjoin(os.getcwd(), 'test/fixtures')


class MonitoringFileFixtures(FileFixtures):
    def __init__(self, sub_dir=''):
        super(MonitoringFileFixtures, self).__init__(
                                                    fixtures_type='monitoring',
                                                    sub_dir=sub_dir)


class RackspaceTests(unittest.TestCase):
    def setUp(self):
        RackspaceMonitoringDriver.connectionCls.conn_classes = (
                RackspaceMockHttp, RackspaceMockHttp)
        RackspaceMonitoringDriver.connectionCls.auth_url = \
                'https://auth.api.example.com/v1.1/'

        RackspaceMockHttp.type = None
        self.driver = RackspaceMonitoringDriver(key=RACKSPACE_PARAMS[0],
                                                secret=RACKSPACE_PARAMS[1],
                ex_force_base_url='http://www.todo.com')

    def test_list_monitoring_zones(self):
        result = list(self.driver.list_monitoring_zones())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 'mzxJ4L2IU')

    def test_list_entities(self):
        result = list(self.driver.list_entities())
        self.assertEqual(len(result), 6)
        self.assertEqual(result[0].id, 'en8B9YwUn6')
        self.assertEqual(result[0].label, 'bar')

    def test_list_checks(self):
        en = self.driver.list_entities()[0]
        result = list(self.driver.list_checks(entity=en))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].label, 'bar')
        self.assertEqual(result[0].details['url'], 'http://www.foo.com')
        self.assertEqual(result[0].details['method'], 'GET')

    def test_list_alarms(self):
        en = self.driver.list_entities()[0]
        result = list(self.driver.list_alarms(entity=en))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, 'remote.http')
        self.assertEqual(result[0].notification_plan_id, 'npIXxOAn5')

    def test_list_check_types(self):
        result = list(self.driver.list_check_types())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, 'remote.dns')
        self.assertTrue(result[0].is_remote)

    def test_list_notification_types(self):
        result = list(self.driver.list_notification_types())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 'webhook')

    def test_list_notifications(self):
        result = list(self.driver.list_notifications())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].type, 'webhook')
        self.assertEqual(result[0].details['url'],
                         'http://www.postbin.org/lulz')

    def test_list_notification_plans(self):
        result = list(self.driver.list_notification_plans())
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0].label, 'test-notification-plan')

    def test_ex_list_alarm_notification_history_checks(self):
        entity = self.driver.list_entities()[0]
        alarm = self.driver.list_alarms(entity=entity)[0]
        result = self.driver.ex_list_alarm_notification_history_checks(
                                                          entity=entity,
                                                          alarm=alarm)
        self.assertEqual(len(result['check_ids']), 2)

    def test_ex_list_alarm_notification_history(self):
        entity = self.driver.list_entities()[0]
        alarm = self.driver.list_alarms(entity=entity)[0]
        check = self.driver.list_checks(entity=entity)[0]
        result = self.driver.ex_list_alarm_notification_history(entity=entity,
                                                     alarm=alarm, check=check)
        self.assertEqual(len(result), 1)
        self.assertTrue('timestamp' in result[0])
        self.assertTrue('notification_plan_id' in result[0])
        self.assertTrue('state' in result[0])
        self.assertTrue('transaction_id' in result[0])
        self.assertTrue('notification_results' in result[0])

    def test_test_alarm(self):
        entity = self.driver.list_entities()[0]
        criteria = ('if (metric[\"code\"] == \"404\") { return CRITICAL, ',
                   ' \"not found\" } return OK')
        check_data = []
        result = self.driver.test_alarm(entity=entity, criteria=criteria,
                                        check_data=check_data)

        self.assertTrue('timestamp' in result[0])
        self.assertTrue('computed_state' in result[0])
        self.assertTrue('status' in result[0])

    def test_check(self):
        entity = self.driver.list_entities()[0]
        check_data = {'label': 'test', 'monitoring_zones': ['mzA'],
                      'target_alias': 'default', 'details': {'url':
                      'http://www.google.com'}, 'type': 'remote.http'}
        result = self.driver.test_check(entity=entity)

        self.assertTrue('available' in result[0])
        self.assertTrue('monitoring_zone_id' in result[0])
        self.assertTrue('available' in result[0])
        self.assertTrue('metrics' in result[0])

    def test_delete_entity_success(self):
        entity = self.driver.list_entities()[0]
        result = self.driver.delete_entity(entity=entity,
                                           ex_delete_children=False)
        self.assertTrue(result)

    def test_delete_entity_children_exist(self):
        entity = self.driver.list_entities()[1]
        RackspaceMockHttp.type = 'CHILDREN_EXIST'

        try:
            self.driver.delete_entity(entity=entity,
                                      ex_delete_children=False)
        except RackspaceMonitoringValidationError:
            pass
        else:
            self.fail('Exception was not thrown')

    def test_delete_check_success(self):
        en = self.driver.list_entities()[0]
        check = self.driver.list_checks(entity=en)[0]
        check.delete()

    def test_delete_alarm(self):
        en = self.driver.list_entities()[0]
        alarm = self.driver.list_alarms(entity=en)[0]
        alarm.delete()

    def test_delete_notification(self):
        notification = self.driver.list_notifications()[0]
        notification.delete()

    def test_delete_notification_plan(self):
        notification_plan = self.driver.list_notification_plans()[0]
        notification_plan.delete()

    def test_list_agent_tokens(self):
        tokens = self.driver.list_agent_tokens()
        fixture = RackspaceMockHttp.fixtures.load('agent_tokens.json')
        fixture_tokens = json.loads(fixture)
        first_token = fixture_tokens["values"][0]["token"]
        self.assertEqual(tokens[0].token, first_token)
        self.assertEqual(len(tokens), 11)

    def test_delete_agent_token(self):
        agent_token = self.driver.list_agent_tokens()[0]
        self.assertTrue(self.driver.delete_agent_token(
          agent_token=agent_token))

    def test_get_monitoring_zone(self):
        monitoring_zone = self.driver \
                              .get_monitoring_zone(monitoring_zone_id='mzord')
        self.assertEqual(monitoring_zone.id, 'mzord')
        self.assertEqual(monitoring_zone.label, 'ord')
        self.assertEqual(monitoring_zone.country_code, 'US')

    def test_ex_traceroute(self):
        monitoring_zone = self.driver.list_monitoring_zones()[0]
        result = self.driver.ex_traceroute(monitoring_zone=monitoring_zone,
                                           target='google.com')
        self.assertEqual(result[0]['number'], 1)
        self.assertEqual(result[0]['rtts'], [0.572, 0.586, 0.683])
        self.assertEqual(result[0]['ip'], '50.57.61.2')

    def test__url_to_obj_ids(self):
        pairs = [
            ['http://127.0.0.1:50000/v1.0/7777/entities/enSTkViNvw',
             {'entity_id': 'enSTkViNvw'}],
            ['https://monitoring.api.rackspacecloud.com/v1.0/7777/entities/enSTkViNvw',
             {'entity_id': 'enSTkViNvw'}],
            ['https://monitoring.api.rackspacecloud.com/v2.0/7777/entities/enSTkViNvu',
             {'entity_id': 'enSTkViNvu'}],
            ['https://monitoring.api.rackspacecloud.com/v2.0/7777/alarms/alfoo',
             {'alarm_id': 'alfoo'}],
            ['https://monitoring.api.rackspacecloud.com/v2.0/7777/entities/enFoo/checks/chBar',
             {'entity_id': 'enFoo', 'check_id': 'chBar'}],
            ['https://monitoring.api.rackspacecloud.com/v2.0/7777/entities/enFoo/alarms/alBar',
             {'entity_id': 'enFoo', 'alarm_id': 'alBar'}],
        ]

        for url, expected in pairs:
            result = self.driver._url_to_obj_ids(url)
            self.assertEqual(result, expected)

    def test_force_base_url(self):
        RackspaceMonitoringDriver.connectionCls.conn_classes = (
                RackspaceMockHttp, RackspaceMockHttp)
        RackspaceMonitoringDriver.connectionCls.auth_url = \
                'https://auth.api.example.com/v1.1/'

        RackspaceMockHttp.type = None
        driver = RackspaceMonitoringDriver(key=RACKSPACE_PARAMS[0],
                                           secret=RACKSPACE_PARAMS[1],
                ex_force_base_url='http://www.todo.com')
        driver.list_entities()
        self.assertEqual(driver.connection._ex_force_base_url,
                         'http://www.todo.com/23213')

    def test_force_base_url_is_none(self):
        RackspaceMonitoringDriver.connectionCls.conn_classes = (
                RackspaceMockHttp, RackspaceMockHttp)
        RackspaceMonitoringDriver.connectionCls.auth_url = \
                'https://auth.api.example.com/v1.1/'

        RackspaceMockHttp.type = None
        driver = RackspaceMonitoringDriver(key=RACKSPACE_PARAMS[0],
                                           secret=RACKSPACE_PARAMS[1])
        driver.list_entities()
        self.assertEqual(driver.connection._ex_force_base_url,
                        'https://monitoring.api.rackspacecloud.com/v1.0/23213')


class RackspaceMockHttp(MockHttpTestCase):
    auth_fixtures = MonitoringFileFixtures('rackspace/auth')
    fixtures = MonitoringFileFixtures('rackspace/v1.0')
    json_content_headers = {'content-type': 'application/json; charset=UTF-8'}

    def _v2_0_tokens(self, method, url, body, headers):
        body = self.auth_fixtures.load('_v2_0_tokens.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_monitoring_zones(self, method, url, body, headers):
        body = self.fixtures.load('monitoring_zones.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_monitoring_zones_mzord(self, method, url, body, headers):
        body = self.fixtures.load('get_monitoring_zone.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_monitoring_zones_mzxJ4L2IU_traceroute(self, method, url, body,
                                                     headers):
        body = self.fixtures.load('ex_traceroute.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities(self, method, url, body, headers):
        body = self.fixtures.load('entities.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_check_types(self, method, url, body, headers):
        body = self.fixtures.load('check_types.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_notification_types(self, method, url, body, headers):
        body = self.fixtures.load('notification_types.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_notifications(self, method, url, body, headers):
        body = self.fixtures.load('notifications.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_notification_plans(self, method, url, body, headers):
        body = self.fixtures.load('notification_plans.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6_checks(self, method, url, body, headers):
        body = self.fixtures.load('checks.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6_alarms(self, method, url, body, headers):
        body = self.fixtures.load('alarms.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6_alarms_aldIpNY8t3_notification_history(self,
                                                             method,
                                                             url, body,
                                                             headers):
        body = self.fixtures.load('list_alarm_history_checks.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6_alarms_aldIpNY8t3_notification_history_chhJwYeArX(self,
                                                             method,
                                                             url, body,
                                                             headers):
        body = self.fixtures.load('list_alarm_history.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6_test_alarm(self, method, url, body,
                                              headers):
        body = self.fixtures.load('test_alarm.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6_test_check(self, method, url, body,
                                              headers):
        body = self.fixtures.load('test_check.json')
        return (httplib.OK, body, self.json_content_headers,
                httplib.responses[httplib.OK])

    def _23213_entities_en8B9YwUn6(self, method, url, body, headers):
        body = ''
        if method == 'DELETE':
            return (httplib.NO_CONTENT, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

        raise NotImplementedError('')

    def _23213_entities_en8Xmk5lv1_CHILDREN_EXIST(self, method, url, body,
                                                  headers):
        if method == 'DELETE':
            body = self.fixtures.load('error_children_exist.json')
            return (httplib.BAD_REQUEST, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

        raise NotImplementedError('')

    def _23213_entities_en8B9YwUn6_checks_chhJwYeArX(self, method, url, body,
                                                     headers):
        if method == 'DELETE':
            body = ''
            return (httplib.NO_CONTENT, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

        raise NotImplementedError('')

    def _23213_entities_en8B9YwUn6_alarms_aldIpNY8t3(self, method, url, body,
                                                     headers):
        if method == 'DELETE':
            body = ''
            return (httplib.NO_CONTENT, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

        raise NotImplementedError('')

    def _23213_notifications_ntQVm5IyiR(self, method, url, body, headers):
        if method == 'DELETE':
            body = ''
            return (httplib.NO_CONTENT, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

        raise NotImplementedError('')

    def _23213_notification_plans_npIXxOAn5(self, method, url, body, headers):
        if method == 'DELETE':
            body = ''
            return (httplib.NO_CONTENT, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

        raise NotImplementedError('')

    def _23213_agent_tokens_at28OJNsRB(self, method, url, body, headers):
        if method == 'DELETE':
            body = ''
            return (httplib.NO_CONTENT, body, self.json_content_headers,
                    httplib.responses[httplib.NO_CONTENT])

    def _23213_agent_tokens(self, method, url, body, headers):
        if method == 'GET':
            body = self.fixtures.load('agent_tokens.json')
            return (httplib.OK, body, self.json_content_headers,
                    httplib.responses[httplib.OK])


if __name__ == '__main__':
    sys.exit(unittest.main())
