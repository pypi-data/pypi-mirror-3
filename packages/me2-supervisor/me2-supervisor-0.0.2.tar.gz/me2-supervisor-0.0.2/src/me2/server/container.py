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

import logging
import json
import threading


from mjsrpc2 import RPCBase, jsonmethod, jsonattribute

from me2.server.storage_manager import BtrfsStorageManager
from me2.server.lxc.execution_manager import LxcExecutionManager

class ContainerManager(RPCBase):
    log = logging.getLogger("ContainerManager")
    def __init__(self, config):
        RPCBase.__init__(self)
        self.btrfs = BtrfsStorageManager(manager = self, config = config.get("storage", {}))
        self.lxc = LxcExecutionManager(manager = self, config = config.get("execution", {}))
        self.config = config
        self.lock = threading.Lock()

    @jsonmethod
    @jsonattribute(name = "bundle_id", kind = str, documentation = "the budle that should be started")
    def start(self, bundle_id):
        with self.lock:
            pass

class Deployer(RPCBase):
    log = logging.getLogger("Deployer")
    def __init__(self, config_file = None):
        RPCBase.__init__(self)
        if config_file is None:
            self.log.info("No config file provided")
            config = {}
        else:
            self.log.debug("Loading config from %s", config_file)
            config = json.load(open(config_file))
        deployer_config = config.get("deployer", {})
        container_manager_config = deployer_config.get("container-manager", {})
        self.add_method('manager', ContainerManager(config = container_manager_config))
