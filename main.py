import time

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch

import webapp2


class SleepHandler(webapp2.RequestHandler):
    def get(self):
        delay = float(self.request.get('delay'))
        time.sleep(delay)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Response delayed by %fs' % delay)


class MainHandler(webapp2.RequestHandler):
    _T = 6

    def __fetch(self, timeout):
        rpc = urlfetch.create_rpc(deadline=timeout)
        urlfetch.make_fetch_call(rpc, '%s/sleep?delay=%f' % (self.request.host_url, timeout))
        return rpc


    def get(self):
        start = time.time()
        sleep1, sleep2 = float(self.request.get('sleep1')), float(self.request.get('sleep2'))
        self.response.headers['Content-Type'] = 'text/plain'
        rpc1, rpc2 = self.__fetch(sleep1), self.__fetch(sleep2)
        result = apiproxy_stub_map.UserRPC.wait_any([rpc1, rpc2])
        finished_in = time.time() - start
        if result is rpc1:
            self.response.write('Finished 1\n')
        elif result is rpc2:
            self.response.write('Finished 2\n')
        else:
            self.response.write('Finished unknown!\n')
        self.response.write('rpc1 status is: %s\n' % rpc1.state)
        self.response.write('rpc2 status is: %s\n' % rpc2.state)
        self.response.write('Finished in %fs\n' % finished_in)


app = webapp2.WSGIApplication([
    ('/sleep', SleepHandler),
    ('/', MainHandler),
], debug=True)
