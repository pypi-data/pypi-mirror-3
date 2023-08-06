# Copyright 2012 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from quantumclient.common import exceptions
from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp
from quantumclient.quantum.v2_0.network import CreateNetwork
from quantumclient.quantum.v2_0.network import ListNetwork
from quantumclient.quantum.v2_0.network import UpdateNetwork
from quantumclient.quantum.v2_0.network import ShowNetwork
from quantumclient.quantum.v2_0.network import DeleteNetwork


class CLITestV20Network(CLITestV20Base):
    def test_create_network(self):
        """ create_net myname"""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_network_tenant(self):
        """create_net --tenant-id tenantid myname"""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--tenant-id', 'tenantid', name]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_network_tags(self):
        """ create_net myname --tags a b"""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name, '--tags', 'a', 'b']
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tags=['a', 'b'])

    def test_create_network_state(self):
        """ create_net --admin-state-down myname"""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--admin-state-down', name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          admin_state_up=False)

    def test_list_nets_detail(self):
        """list_nets -D"""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_nets_tags(self):
        """list_nets -- --tags a b"""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_nets_detail_tags(self):
        """list_nets -D -- --tags a b"""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_nets_fields(self):
        """list_nets --fields a --fields b -- --fields c d"""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def test_update_network_exception(self):
        """ update_net myid"""
        resource = 'network'
        cmd = UpdateNetwork(MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_update_network(self):
        """ update_net myid --name myname --tags a b"""
        resource = 'network'
        cmd = UpdateNetwork(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_show_network(self):
        """ show_net --fields id --fields name myid """
        resource = 'network'
        cmd = ShowNetwork(MyApp(sys.stdout), None)
        myid = 'myid'
        args = ['--fields', 'id', '--fields', 'name', myid]
        self._test_show_resource(resource, cmd, myid, args, ['id', 'name'])

    def test_delete_network(self):
        """
        delete_net myid
        """
        resource = 'network'
        cmd = DeleteNetwork(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
