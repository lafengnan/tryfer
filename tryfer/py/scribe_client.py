# Copyright 2012 Rackspace Hosting, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading

from thrift import Thrift

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from tryfer._thrift.scribe.scribe import Client
from tryfer._thrift.scribe.ttypes import LogEntry


class ScribeClient(object):
    def __init__(self, host, port):
        self._transport = TTransport.TFramedTransport(
            TSocket.TSocket(host, port))

        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(
            trans=self._transport, strictRead=False, strictWrite=False)

        self._client = Client(protocol)
        self._lock = threading.Lock()

    def log(self, category, messages):
        self._lock.acquire()

        if not self._transport.isOpen():
            self._transport.open()

        try:
            self._client.Log(
                [LogEntry(category, message) for message in messages])
        except Thrift.TException:
            self._transport.close()
        except Exception:
            self._transport.close()
        finally:
            self._lock.release()


if __name__ == '__main__':
    c = ScribeClient('localhost', 61686)

    c.log("foo", ["bar"])

    c.log("foo", ["baz", "bax"])

    import time
    time.sleep(60)

    c.log("bar", ["quux"])
