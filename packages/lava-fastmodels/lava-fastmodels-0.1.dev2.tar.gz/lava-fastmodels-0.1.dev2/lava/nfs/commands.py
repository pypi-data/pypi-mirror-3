# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Fast Models
#
# LAVA Fast Models is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Fast Models is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Fast Models.  If not, see <http://www.gnu.org/licenses/>.

import sys

from lava_tool.interface import Command, SubCommand, LavaCommandError
from lava.nfs.backend import Entry, Service


class NFSCommand(SubCommand):
    """
    Interact with NFS exports
    """

    namespace = "lava.nfs.commands"

    @classmethod
    def get_name(cls):
        return "nfs"


class ExportCommand(Command):
    """
    Export a directory over NFS
    """

    @classmethod
    def get_name(cls):
        return "export"

    @classmethod
    def register_arguments(cls, parser):
        super(ExportCommand, cls).register_arguments(parser)
        parser.add_argument(
            "path",
            metavar="PATH",
            help="Filesystem path to export"),
        parser.add_argument(
            "client",
            metavar="CLIENT",
            help="NFS client definition, see export(5)")

    def _get_nfs_options(self):
        return ['async', 'no_subtree_check', 'no_root_squash']

    def invoke(self):
        entry = {
            'path': self.args.path,
            'clients': [{
                'client': self.args.client,
                'options': self._get_nfs_options()
            }]
        }
        service = Service()
        with service:
            service.add_entry(entry)


class UnExportCommand(Command):
    """
    Remove an existing export
    """

    @classmethod
    def get_name(cls):
        return "unexport"

    @classmethod
    def register_arguments(cls, parser):
        super(UnExportCommand, cls).register_arguments(parser)
        parser.add_argument(
            "path",
            metavar="PATH",
            help="Filesystem path to export"),

    def invoke(self):
        raise LavaCommandError("not implemented (yet)")
