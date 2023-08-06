# Author: Joseph Lawson <joe@joekiller.com>
# Copyright 2012 Joseph Lawson.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from alertlogic import *

class AlertLogicApiTester(unittest.TestCase):

    def setUp(self):
        print('setUp AlertLogicApiTester')
        self.access_token = ''
        self.secret_key = ''
        self.domain = 'cloud.alertlogic.com'
        self.connection = AlertLogicConnection(self.access_token,self.secret_key,self.domain)
        print('Using connection %s.' % connection)

class GetAlertLogicAppliances(AlertLogicApiTester):
    def runTest(self):
        print('Trying to get all appliances.')
        appliances = self.connection.get_all_appliances()
        for appliance in appliances:
            print('Got appliance: %s with instance id: %s' % (appliance.appliance_id, appliance.instance_id))
        assert True

class GetAlertLogicHosts(AlertLogicApiTester):
    def runTest(self):
        print('Trying to get all hosts.')
        hosts = self.connection.get_all_hosts()
        for host in hosts:
            print('Got host: %s with instance id: %s' %(host.host_id, host.instance_id))
        assert True


