# Copyright (C) 2012 Linaro Limited
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

"""
lava.nfs.backend
================

Backend for working with NFS shares. Instantiate
:class:`~lava.nfs.backend.Service` and use the methods it provides to configure
NFS shares.

Parts of API in this module were created based on exports(5) man page. Reading
that manual page may help you understand some of the terms.
"""

import subprocess

from json_document import bridge
from json_document.document import Document, DocumentFragment
from json_document.shortcuts import persistence


class _Entry(DocumentFragment):
    """
    Entry in a NFS export definition

    Represents a single entry describing how to export a particular
    path to an arbitrary list of clients
    """

    @bridge.readwrite
    def path(self):
        """
        The filesystem pathname to export 
        """

    @bridge.fragment
    def clients(self):
        """
        An array of client definitions.
        """

    def __unicode__(self):
        """
        Format this export definition as a single line suitable for /etc/exports
        """
        return u"{path} {clients}".format(path=self.path, clients=self.clients)


class _ClientList(DocumentFragment):
    """
    List of NFS client definitions
    """

    def __unicode__(self):
        """
        Format this list of clients as a part of /etc/exports entry
        """
        return u" ".join([unicode(client) for client in self])


class _Client(DocumentFragment):
    """
    Single NFS client definition.

    A client (in NFS-nomenclature) is a definition of a host or a
    group of hosts that share nfs mount options.
    """

    @bridge.readwrite
    def client(self):
        """
        Client definition.

        It can be specified in a few ways:

            1) single host
            2) IP networks
            3) wildcards (using glob-like syntax)
            4) netgroups
            5) anonymous

        For full details refer to the exports(5) manual page
        """

    @bridge.readwrite
    def options(self):
        """
        Export options for this client
        """

    def __unicode__(self):
        """
        Format this client definition as a part of /etc/exports entry
        """
        if self.options:
            return u"{client}({options})".format(
                client=self.client,
                options=",".join(self.options))
        else:
            return self.client



class _EntryList(Document):
    """
    Document representing a list of entries in a /etc/exports file
    """

    document_schema = {
        'type': 'array',
        'default': [],
        'items': {
            '__fragment_cls': _Entry,
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                },
                'clients': {
                    '__fragment_cls': _ClientList,
                    'type': 'array',
                    'items': {
                        '__fragment_cls': _Client,
                        'type': 'object',
                        'properties': {
                            'client': {
                                'type': 'string',
                            },
                            'options': {
                                'type': 'array',
                                'unique': True,
                                'default': [],
                                'items': {
                                    'type': 'string',
                                    'enum': [
                                        # Not all options are supported, options
                                        # with arguments option=value were discarded
                                        'secure', 'rw', 'async', 'sync',
                                        'no_wdelay', 'nohide', 'crossmnt',
                                        'no_subtree_check', 'insecure_locks',
                                        'no_auth_nlm', 'no_acl', 'mountpoint',
                                        'root_squash', 'no_root_squash',
                                        'all_suqash', 'anonuid', 'anongid']
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    def append(self, entry):
        """
        Add an entry to the export list
        """
        self.value.append(entry)
        # This is sadly needed because we modify the document in a
        # way that is invisible to the wrapper classes.
        self._bump_revision()


class _ExportsSerializer(object):
    """
    Serializer that creates files compatible with /etc/exports

    This serializer is somewhat special that it expects the object-oriented
    wrapper (EntryList) and not the raw json object.
    """

    # This code depends on the EntryList and fragment __unicode__ methods to work
    needs_real_object = True

    @classmethod
    def dumps(cls, obj):
        if not isinstance(obj, _EntryList):
            raise TypeError(
                "ExportsSerializer.dumps() requires a EntrtList instance as argument")
        return "\n".join(
            [
                "# DO NOT EDIT!",
                "# This file was automatically generated by the LAVA NFS service",
                "# To manipulate it, please use `lava nfs export` and `lava nfs unexport`",
                "",
            ] + [
                unicode(entry) 
                for entry in sorted(obj, key=lambda entry: entry.path)
            ])

    @classmethod
    def loads(cls, text):
        raise NotImplementedError(
            "Parsing of files compatible with /etc/exports is not supported")


class Service(object):
    """
    Wrapper around system NFS service

    The machine readable definitions are kept in ``/etc/lava/nfs/exports.json``
    They are modified and saved back. In addition this triggers an overwrite of
    ``/etc/exports.d/lava.exports`` that contains the expected NFS friendly
    syntax and a reload of the NFS service.

    .. warning::

        Currently this service runs directly from python. This is insecure
        (requires ``sudo`` which can be used for other activities), racy (two
        concurrent NFS service may damage each other and produce inconsistent
        state). Eventually we want to support a new command ``lava nfs
        service`` that would run as root and encapsulate all of those
        activities while exporting only a socket-based interface to communicate
        with clients. The socket could be used to provide security checks and would
        allow the clients to run as unprivileged users.
    """

    # TODO: Bootstrapping problem: how to export something in
    # practice We need two entries in /etc and we need to call
    # exports -r

    LAVA_FILE = "/etc/lava/nfs/exports.json"
    NFS_FILE = "/etc/exports.d/lava.exports"

    def __init__(self):
        """
        Initialize NFS service.

        This loads the json representation of expected NFS shares at startup.
        It does not currently prevent multiple services from colliding. 
        """
        self._entries = EntryList([])
        self._js_persistence = persistence(
            self._entries, self.LAVA_FILE)
        self._nfs_persistence = persistence(
            self._entries, self.NFS_FILE, serializer=ExportsSerializer)

    def _lock(self):
        # TODO: Acquire global fs lock here
        pass

    def _unlock(self):
        pass

    def __enter__(self):
        self._lock()
        self._js_persistence.load()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._js_persistence.is_dirty:
            self._js_persistence.save()
            self._nfs_persistence.save()
            self._call_exports_r()
        self._unlock()

    def _call_exports_r(self):
        # TODO: convert to a service IPC to lava nfs monitor
        subprocess.check_call(['sudo', 'exportfs', '-r'])

    def add_entry(self, entry):
        """
        Add an entry to be exported in the local NFS server.

        The entry is a dictionary with two keys, ``path`` and ``clients``. Path
        must be a valid filesystem path to export. Clients must be an array of
        client definitions. Each client definition is a dictionary composed of
        two items: ``client`` defines the client string (like an IP address,
        network or hostname) while ``options`` define the NFS export option
        list.

        For example, the following code would export the  ``/home/`` directory
        to all machines on a typical local network:: 

            service.add_entry({
                "path": "/home/",
                "clients": [{
                    "client": "192.168.1.0/24",
                    "options": ["async", "no_root_squash", "rw"]
                }]
            })
        """
        self._entries.append(entry)

    def remove_entry(self, path):
        raise NotImplementedError()
