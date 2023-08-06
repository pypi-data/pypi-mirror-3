# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
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

"""
Instance Deferred Delete Extension
"""
from novaclient import base
from novaclient import utils
from novaclient.v1_1 import servers


def restore(self, server):
    """
    Restore a deferred deleted instance.

    :param server: The :class:`Server` (or its ID).
    :returns Newly created :class:`Image` object
    """
    data = {}
    self._action('restore', server, data)


servers.ServerManager.restore = restore


def restore(self):
    """
    Restore a deferred deleted instance.

    :returns Newly created :class:`Image` object
    """
    return self.manager.restore(self)


servers.Server.restore = restore


@utils.arg('server', metavar='<server>', help='Name or ID of server.')
def do_restore(cs, args):
    """Restore a deferred deleted server."""
    server = utils.find_resource(cs.servers, args.server)
    server.restore()


def force_delete(self, server):
    """
    Force delete a deferred deleted instance.

    :param server: The :class:`Server` (or its ID).
    :returns Newly created :class:`Image` object
    """
    data = {}
    self._action('forceDelete', server, data)


servers.ServerManager.force_delete = force_delete


def force_delete(self):
    """
    Force delete a deferred deleted instance.

    :returns Newly created :class:`Image` object
    """
    return self.manager.force_delete(self)


servers.Server.force_delete = force_delete


@utils.arg('server', metavar='<server>', help='Name or ID of server.')
def do_force_delete(cs, args):
    """Force delete a deferred deleted server."""
    server = utils.find_resource(cs.servers, args.server)
    server.force_delete()
