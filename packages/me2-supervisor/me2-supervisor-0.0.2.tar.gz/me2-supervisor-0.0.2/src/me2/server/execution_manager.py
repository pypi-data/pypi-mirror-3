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

import threading
import logging
from mjsrpc2 import RPCBase, jsonmethod, jsonattribute

class ExecutionManagerBase(RPCBase):
    log = logging.getLogger("ExecutionManagerBase")
    lock = threading.Lock()
    def __init__(self, manager, config):
        super(ExecutionManagerBase, self).__init__()
        self._manager = manager
        self.config = config

    @jsonmethod
    @jsonattribute(name = "bottle", documentation = "The bottle in which the container should be started")
    @jsonattribute(name = "name", documentation = "Container Name")
    def start(self, bottle, name):
        with self.lock:
            pass


