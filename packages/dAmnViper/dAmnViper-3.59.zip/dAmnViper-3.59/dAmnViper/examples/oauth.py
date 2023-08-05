''' Example usage of oAuth objects.
    Created by photofroggy.
'''

import os
import sys
from twisted.internet import reactor

sys.path.insert(0, os.curdir)

from dAmnViper.dA import oauth

def stop(response):
    print 'ok so yeah'
    reactor.stop()
    return response

client = oauth.oAuthClient(reactor, 80)
client.serve().addCallback(stop)

reactor.run()

# EOF
