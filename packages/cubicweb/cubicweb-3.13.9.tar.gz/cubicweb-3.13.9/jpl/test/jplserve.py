"""simple script to start a test server"""
import socket

from twisted.application import service, strports
# from twisted.internet import reactor, task
from twisted.web2 import channel
from twisted.web2 import server
from twisted.internet import reactor

from cubicweb.devtools import ApptestConfiguration
from cubicweb.etwist.server import CubicWebRootResource

PORT = 7777

def get_starturl(logged=True):
    if logged:
        return 'http://%s:%s/view?login=admin&password=gingkow' % (socket.gethostname(), PORT)
    else:
        return 'http://%s:%s' % (socket.gethostname(), PORT)
    
def make_site():
    from cubicweb.cubicwebconfig import CubicWebConfiguration
    from cubicweb.etwist import twconfig # trigger configuration registration
    config = ApptestConfiguration('data')
    base_url = get_starturl(logged=False)
    print "base url =", base_url
    # if '-n' in sys.argv: # debug mode
    cubicweb = CubicWebRootResource(config, base_url, debug=True)
    toplevel = cubicweb
    website = server.Site(toplevel)
    return channel.HTTPFactory(website)


def runserver():
    reactor.listenTCP(PORT, make_site())
    print "ready"
    reactor.run()


if __name__ == '__main__':
    runserver()
