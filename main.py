import time

from google.appengine.ext import ndb
from google.appengine.ext.ndb import eventloop

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
        sleep1 = float(self.request.get('sleep1'))
        self.response.headers['Content-Type'] = 'text/plain'
        context = ndb.get_context()
        rpc1 = context.urlfetch('%s/sleep?delay=%f' % (self.request.host_url, sleep1), deadline=sleep1*2)
        end = start + sleep1
        ev = eventloop.get_event_loop()
        while time.time() < end:
            ev.run1()
            if rpc1.done():
                break
            time.sleep(0.01)
        finished_in = time.time() - start
        self.response.write('rpc1 status is: %s\n' % rpc1.state)
        self.response.write('Finished in %fs\n' % finished_in)


app = webapp2.WSGIApplication([
    ('/sleep', SleepHandler),
    ('/', MainHandler),
], debug=True)
