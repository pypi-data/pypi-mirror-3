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
                                          'PREF=ID=cdba111a2d8e9691:FF=0:TM=1302639575:LM=1302639575:S=hIVLRDkC_-wblcYj; expires=Thu, 11-Apr-2013 20:19:35 GMT; path=/; domain=.google.com, NID=45=4byZmb0wMTiPXe_RHVX2Fo_CPLZ2uk1T-zZgrsi6q8JAkD6NyDVY12kgNWPaGeh8G2K-hiOpu3PsvdRAE3XFdMrlC__TJ60wXSNNNikBLdoCXICc-ld_vVcE16UX-x2U; expires=Wed, 12-Oct-2011 20:19:35 GMT; path=/; domain=.google.com; HttpOnly'),
                     ('expires', '-1'),
                     ('server', 'gws'),
                     ('cache-control', 'private, max-age=0'),
                     ('date', 'Tue, 12 Apr 2011 20:19:35 GMT'),
                     ('content-type', 'text/html; charset=ISO-8859-1')],
        'body': FileWrapper('step_0_response.txt', here),
        'status': 200,
        'reason': 'OK',
        'version': 11,
    }
    next_step = 'None'
    
    def handle_request(self, request):
        assert dalton.request_match(request, self.recorded_request)
        return (self.next_step, dalton.create_response(self.recorded_response))

