import os
import dalton
from dalton import FileWrapper

here = os.path.abspath(os.path.dirname(__file__))

class StepNumber0(object):
    recorded_request = {
        'headers':  {},
        'url': '/',
        'method': 'GET',
        'body': None,
    }
    recorded_response = {
        'headers':  [('x-xss-protection', '1; mode=block'),
                     ('transfer-encoding', 'chunked'),
                     (                    'set-cookie',
                                          'PREF=ID=52484a4634608d1e:FF=0:TM=1318720603:LM=1318720603:S=X_NZZf8Nt_oFQxjz; expires=Mon, 14-Oct-2013 23:16:43 GMT; path=/; domain=.google.com, NID=52=gJ_ydKjpsDeuX4PWUy_yi-TxmF4w0BC7U0W0dqooHiGUZlraJnJLR1qQ20TU4ixlRPx7L16VXD8BNZiY74WaVMFgaxYMUcrBBYNkSZcw6mX9M-G_RGNkWlSw66xa9adI; expires=Sun, 15-Apr-2012 23:16:43 GMT; path=/; domain=.google.com; HttpOnly'),
                     ('expires', '-1'),
                     ('server', 'gws'),
                     ('cache-control', 'private, max-age=0'),
                     ('date', 'Sat, 15 Oct 2011 23:16:43 GMT'),
                     ('x-frame-options', 'SAMEORIGIN'),
                     ('content-type', 'text/html; charset=ISO-8859-1')],
        'body': FileWrapper('step_0_response.txt', here),
        'status': 200,
        'reason': 'OK',
        'version': 11,
    }
    next_step = 'StepNumber1'
    
    def handle_request(self, request):
        assert dalton.request_match(request, self.recorded_request)
        return (self.next_step, dalton.create_response(self.recorded_response))


class StepNumber1(object):
    recorded_request = {
        'headers':  {},
        'url': '/',
        'method': 'POST',
        'body': FileWrapper('step_1_request.txt', here),
    }
    recorded_response = {
        'headers':  [('content-length', '11816'),
                     ('x-xss-protection', '1; mode=block'),
                     ('server', 'gws'),
                     ('allow', 'GET, HEAD'),
                     ('date', 'Sat, 15 Oct 2011 23:16:43 GMT'),
                     ('x-frame-options', 'SAMEORIGIN'),
                     ('content-type', 'text/html; charset=UTF-8')],
        'body': FileWrapper('step_1_response.txt', here),
        'status': 405,
        'reason': 'Method Not Allowed',
        'version': 11,
    }
    next_step = 'None'
    
    def handle_request(self, request):
        assert dalton.request_match(request, self.recorded_request)
        return (self.next_step, dalton.create_response(self.recorded_response))

