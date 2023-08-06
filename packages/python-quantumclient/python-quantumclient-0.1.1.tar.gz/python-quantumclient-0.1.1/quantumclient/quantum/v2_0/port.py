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

import logging

from quantumclient import utils
from quantumclient.quantum.v2_0 import CreateCommand
from quantumclient.quantum.v2_0 import DeleteCommand
from quantumclient.quantum.v2_0 import ListCommand
from quantumclient.quantum.v2_0 import ShowCommand
from quantumclient.quantum.v2_0 import UpdateCommand


def _format_fixed_ips(port):
    try:
        return '\n'.join([utils.dumps(ip) for ip in port['fixed_ips']])
    except Exception:
        return ''


class ListPort(ListCommand):
    """List networks that belong to a given tenant

    Sample: list_ports -D -- --name=test4 --tag a b
    """

    resource = 'port'
    log = logging.getLogger(__name__ + '.ListPort')
    _formatters = {'fixed_ips': _format_fixed_ips, }


class ShowPort(ShowCommand):
    """Show information of a given port

    Sample: show_port -D <port_id>
    """

    resource = 'port'
    log = logging.getLogger(__name__ + '.ShowPort')


class CreatePort(CreateCommand):
    """Create a port for a given tenant

    Sample create_port --tenant-id xxx --admin-state-down \
      --mac_address mac --device_id deviceid <network_id>

    """

    resource = 'port'
    log = logging.getLogger(__name__ + '.CreatePort')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='set admin state up to false')
        parser.add_argument(
            '--mac-address',
            help='mac address of port')
        parser.add_argument(
            '--device-id',
            help='device id of this port')
        parser.add_argument(
            '--fixed-ip',
            action='append',
            help='desired Ip for this port: '
            'subnet_id=<id>,ip_address=<ip>, '
            'can be repeated')
        parser.add_argument(
            'network_id',
            help='Network id of this port belongs to')

    def args2body(self, parsed_args):
        body = {'port': {'admin_state_up': parsed_args.admin_state_down,
                         'network_id': parsed_args.network_id, }, }
        if parsed_args.mac_address:
            body['port'].update({'mac_address': parsed_args.mac_address})
        if parsed_args.device_id:
            body['port'].update({'device_id': parsed_args.device_id})
        if parsed_args.tenant_id:
            body['port'].update({'tenant_id': parsed_args.tenant_id})
        ips = []
        if parsed_args.fixed_ip:
            for ip_spec in parsed_args.fixed_ip:
                ips.append(utils.str2dict(ip_spec))
        if ips:
            body['port'].update({'fixed_ips': ips})
        return body


class DeletePort(DeleteCommand):
    """Delete a given port

    Sample: delete_port <port_id>
    """

    resource = 'port'
    log = logging.getLogger(__name__ + '.DeletePort')


class UpdatePort(UpdateCommand):
    """Update port's information

    Sample: update_port <port_id> --name=test --admin_state_up type=bool True
    """

    resource = 'port'
    log = logging.getLogger(__name__ + '.UpdatePort')
