""" Example6 WSGI Server.
    Use GWSGIServer.
"""

from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_wsgi_server import GWSGIServer

#===============================================================
#                   Server
#===============================================================


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello World\n'


class GPrincipal(GObj):
    """  Server Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, {})

    def start_up(self):
        self.wsgiserver = self.create_gobj(
            None,
            GWSGIServer,
            self,
            host='0.0.0.0',
            port=8000,
            application=application)
        self.set_trace_mach(True, pprint, level=-1)


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    ga_srv = GAplic('Example6')
    ga_srv.create_gobj('principal', GPrincipal, None)

    try:
        ga_srv.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
