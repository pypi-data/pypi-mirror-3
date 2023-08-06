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

from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp
from quantumclient.quantum.v2_0.subnet import CreateSubnet
from quantumclient.quantum.v2_0.subnet import ListSubnet
from quantumclient.quantum.v2_0.subnet import UpdateSubnet
from quantumclient.quantum.v2_0.subnet import ShowSubnet
from quantumclient.quantum.v2_0.subnet import DeleteSubnet


class CLITestV20Subnet(CLITestV20Base):

    def test_create_subnet(self):
        """ create_subnet --gateway gateway netid cidr"""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        gateway = 'gatewayvalue'
        args = ['--gateway', gateway, netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, ]
        position_values.extend([netid, cidr, gateway])
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_subnet_tenant(self):
        """create_subnet --tenant-id tenantid netid cidr"""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant-id', 'tenantid', netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr']
        position_values = [4, ]
        position_values.extend([netid, cidr])
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_subnet_tags(self):
        """ create_subnet netid cidr --tags a b"""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = [netid, cidr, '--tags', 'a', 'b']
        position_names = ['ip_version', 'network_id', 'cidr']
        position_values = [4, ]
        position_values.extend([netid, cidr])
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tags=['a', 'b'])

    def test_list_subnets_detail(self):
        """list_subnets -D"""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_subnets_tags(self):
        """list_subnets -- --tags a b"""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_subnets_detail_tags(self):
        """list_subnets -D -- --tags a b"""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_subnets_fields(self):
        """list_subnets --fields a --fields b -- --fields c d"""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def test_update_subnet(self):
        """ update_subnet myid --name myname --tags a b"""
        resource = 'subnet'
        cmd = UpdateSubnet(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_show_subnet(self):
        """ show_subnet --fields id --fields name myid """
        resource = 'subnet'
        cmd = ShowSubnet(MyApp(sys.stdout), None)
        myid = 'myid'
        args = ['--fields', 'id', '--fields', 'name', myid]
        self._test_show_resource(resource, cmd, myid, args, ['id', 'name'])

    def test_delete_subnet(self):
        """
        delete_subnet myid
        """
        resource = 'subnet'
        cmd = DeleteSubnet(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
