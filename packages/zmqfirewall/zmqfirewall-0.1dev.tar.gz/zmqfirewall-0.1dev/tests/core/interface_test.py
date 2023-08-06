import zmqfirewall.filters
from zmqfirewall.actions import DropMessageAction, AcceptMessageAction, FilterTopicAction
from zmqfirewall.core.interface import *
from zmqfirewall.core.reactor import reactor

from nose.tools import eq_

from tests.helper import Message

import zmq

from pprint import pprint

class SubInterface(Interface):
    connection_uri = 'sub-ipc://testpub'
    name = 'subtest'
    topics = ['']
    filter = (lambda x: pprint(x))

class PubInterface(Interface):
    connection_uri = 'pub-ipc://testpub'
    name = 'pubtest'
    
def test_pubsubinterfaces():
    reactor.callLater(5, PubInterface.publish, 'herp', 'derp')
    reactor.run()
