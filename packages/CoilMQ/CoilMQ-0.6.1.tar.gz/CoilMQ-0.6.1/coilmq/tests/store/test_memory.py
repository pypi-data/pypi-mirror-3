"""
Test memory queue storage.
"""
import unittest
import uuid

from stompclient.frame import Frame

from coilmq.store.memory import MemoryQueue

from coilmq.tests.store import CommonQueueTestsMixin

__authors__ = ['"Hans Lellelid" <hans@xmpl.org>']
__copyright__ = "Copyright 2009 Hans Lellelid"
__license__ = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 
  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

class MemoryQueueTest(CommonQueueTestsMixin, unittest.TestCase):
    
    def setUp(self):
        self.store = MemoryQueue()
        
    def test_dequeue_identity(self):
        """ Test the dequeue() method. """
        dest = '/queue/foo'
        frame = Frame('MESSAGE', headers={'message-id': str(uuid.uuid4())}, body='some data') 
        self.store.enqueue(dest, frame)
        
        assert self.store.has_frames(dest) == True
        assert self.store.size(dest) == 1
        
        rframe = self.store.dequeue(dest)
        assert frame == rframe
        assert frame is rframe # Currently we expect these to be the /same/ object.  
        
        assert self.store.has_frames(dest) == False
        assert self.store.size(dest) == 0
        
