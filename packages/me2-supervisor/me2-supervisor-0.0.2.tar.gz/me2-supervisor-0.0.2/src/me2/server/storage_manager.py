'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import os
import uuid
import logging
import shutil
import pipes
import subprocess

from mjsrpc2 import RPCBase, jsonmethod, jsonattribute

from me2.server.util import OperationResult, ContainerManagerException

class ContainerBottle(object):
    uuid = None
    path = None
    rootfs = None
    configdir = None

class StorageManagerException(ContainerManagerException, IOError):
    pass

class StorageManagerBase(RPCBase):
    log = logging.getLogger("StorageManagerBase")
    def __init__(self, manager, config):
        RPCBase.__init__(self)
        self.config = config
        self._manager = manager
        self.root_directory = config.get("root-directory")
        base_directory = config.get("base-directory", "base")
        instances_directory = config.get("instances-directory", 'instances')
        self.base_directory = os.path.join(self.root_directory, base_directory)
        self.instances_directory = os.path.join(self.root_directory, instances_directory)
        self.log.debug("Root-directory: %s", self.root_directory)
        self.log.debug("Base-directory: %s", self.base_directory)
        self.log.debug("Instances directory: %s", self.instances_directory)

    def isbottle(self, directory):
        if not os.path.exists(directory): return False
        if not os.path.exists(os.path.join(directory, "config")): return False
        if not os.path.exists(os.path.join(directory, "rootfs")): return False
        try:
            uuid.UUID(os.path.basename(directory))
        except ValueError:
            return False

        parent_link = os.path.join(directory, "base")
        if not os.path.exists(parent_link): return False
        return True

    @jsonmethod
    def list_base_bottles(self):
        result = OperationResult()
        bottles = os.listdir(self.base_directory)
        result.status = True
        result.result = bottles
        return vars(result)

    @jsonmethod
    def list_bottles(self):
        response = OperationResult()
        bottle_names = [ subdir for subdir in os.listdir(self.instances_directory) if self.isbottle(os.path.join(self.instances_directory, subdir))]
        bottles = []
        for name in bottle_names[:]:
            bottle = {}
            bottle["uuid"] = str(uuid.UUID(name))
            base = os.path.basename(os.path.realpath(os.path.join(self.instances_directory, name, "base")))
            bottle["base-bottle"] = base
            bottles.append(bottle)
        response.status = True
        response.result = bottles
        return vars(response)

    @jsonmethod
    @jsonattribute(name = "base")
    def clone(self, base, bottle_id = None):
        bottle = ContainerBottle()
        if bottle_id is None:
            bottle_id = uuid.uuid4().get_hex()

        bottle.uuid = bottle_id
        clone_path = os.path.join(self.instances_directory, bottle_id)
        if os.path.exists(clone_path):
            raise StorageManagerException("Bottle already exists")
        bottle.path = clone_path
        bottle.rootfs = os.path.join(bottle.path, "rootfs")
        bottle.configdir = os.path.join(bottle.path, "config")

        self.log.debug("Creating a new bottle in %s", bottle.path)
        os.makedirs(bottle.path)
        os.makedirs(bottle.configdir)
        base_container_path = os.path.join(self.base_directory, base)
        self.create_snapshot(base_container_path, bottle.rootfs)
        os.symlink(base_container_path, os.path.join(bottle.path, "base"))
        return vars(bottle)

    @jsonmethod
    @jsonattribute(name = "bottle_id", kind = str)
    def remove(self, bottle_id):
        bottle_path = os.path.join(self.instances_directory, bottle_id)
        rootfs_path = os.path.join(bottle_path, "rootfs")
        try:
            assert self.isbottle(bottle_path)
            self.delete_snapshot(rootfs_path)
            shutil.rmtree(bottle_path)
        except:
            self.log.exception("Exception trying to remove bottle %s" % bottle_id)
            return False
        return True

    def create_snapshot(self, source, destination):
        """Creates a snapshot of source in destination
        
        @param source: The source that should be snapshot
        @param destination: The directory where the snapshot should go
        """
        raise NotImplementedError()

    def delete_snapshot(self, path):
        """Deletes a snapshot
        
        @param path: The path to the snapshot
        """
        raise NotImplementedError()

class BtrfsStorageManager(StorageManagerBase):
    log = logging.getLogger("BtrfsStorageManager")
    def __init__(self, *args, **kw):
        StorageManagerBase.__init__(self, *args, **kw)

    def create_snapshot(self, source, destination):
        self.log.debug("Creating BTRFS snapshot from %s to %s", source, destination)
        command = self.config.get('storage', {}).get("create-snapshot") % {'source_path': pipes.quote(source),
                                                                           'destination_path': pipes.quote(destination)}
        elevate_privileges = self.config.get('elevate-privileges', None)
        if elevate_privileges:
            command = elevate_privileges % {"command": command}
        self.log.debug("Command to be executed: %s", command)
        subprocess.check_call(command, shell = True)

    def delete_snapshot(self, path):
        #ToDo: I should check that the absolute path is inside the base directory
        self.log.debug("Deleting BTRFS snapshot from %s", path)
        command = self.config.get('storage', {}).get('delete-snapshot') % {'path': pipes.quote(path)}
        elevate_privileges = self.config.get('elevate-privileges', None)
        if elevate_privileges:
            command = elevate_privileges % {"command": command}
        self.log.debug("Command to be executed: %s", command)
        subprocess.check_call(command, shell = True)
