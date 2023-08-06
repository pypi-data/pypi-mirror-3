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
Instance Backup extension
"""
from novaclient import base
from novaclient import utils
from novaclient.v1_1 import servers


def backup(self, server, image_name, backup_type, rotation):
    """
    Create a server backup.

    :param server: The :class:`Server` (or its ID).
    :param image_name: The name to assign the newly create image.
    :param backup_type: 'daily' or 'weekly'
    :param rotation: number of backups of type 'backup_type' to keep
    :returns Newly created :class:`Image` object
    """
    if not rotation:
        raise Exception("rotation is required for backups")
    elif not backup_type:
        raise Exception("backup_type required for backups")
    elif backup_type not in ("daily", "weekly"):
        raise Exception("Invalid backup_type: must be daily or weekly")

    data = {
        "name": image_name,
        "rotation": rotation,
        "backup_type": backup_type,
    }

    self._action('createBackup', server, data)


servers.ServerManager.backup = backup


def backup(self, image_name, backup_type, rotation):
    """
    Create a server backup.

    :param server: The :class:`Server` (or its ID).
    :param image_name: The name to assign the newly create image.
    :param backup_type: 'daily' or 'weekly'
    :param rotation: number of backups of type 'backup_type' to keep
    :returns Newly created :class:`Image` object
    """
    return self.manager.backup(self, image_name, backup_type, rotation)


servers.Server.backup = backup


@utils.arg('server', metavar='<server>', help='Name or ID of server.')
@utils.arg('name', metavar='<name>', help='Name of snapshot.')
@utils.arg('backup_type', metavar='<daily|weekly>', help='type of backup')
@utils.arg('rotation', type=int, metavar='<rotation>',
           help="Number of backups to retain. Used for backup image_type.")
def do_backup(cs, args):
    """Backup a server."""
    server = utils.find_resource(cs.servers, args.server)
    server.backup(args.name, args.backup_type, args.rotation)
