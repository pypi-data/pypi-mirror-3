"""
Copyright 2011 Mozes, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import unittest

from stompest.simple import Stomp

class SimpleStompIntegrationTest(unittest.TestCase):
    DEST = '/queue/stompUnitTest'
    
    def setUp(self):
        stomp = Stomp('localhost', 61613)
        stomp.connect()
        stomp.subscribe(self.DEST, {'ack': 'client'})
        while (stomp.canRead(1)):
            stomp.ack(stomp.receiveFrame())
        
    def test_integration(self):
        stomp = Stomp('localhost', 61613)
        stomp.connect()
        stomp.send(self.DEST, 'test message1')
        stomp.send(self.DEST, 'test message2')
        self.assertFalse(stomp.canRead(1))
        stomp.subscribe(self.DEST, {'ack': 'client'})
        self.assertTrue(stomp.canRead(1))
        frame = stomp.receiveFrame()
        stomp.ack(frame)
        self.assertTrue(stomp.canRead(1))
        frame = stomp.receiveFrame()
        stomp.ack(frame)
        self.assertFalse(stomp.canRead(1))
        stomp.disconnect()

if __name__ == '__main__':
    unittest.main()