import json, urllib2, sys, os
from functools import partial
from bottle import Bottle, route, run, request, response, abort, error

egg_cache = "/path/to/web/egg_cache"
os.environ['PYTHON_EGG_CACHE'] = egg_cache

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.dirname(__file__))

from loader import ManifestReader


class Validator(object):
    def fetch(self, url):
        # print url
        try:
            wh = urllib2.urlopen(url)
        except urllib2.HTTPError, wh:
            pass
        data = wh.read()
        wh.close()
        return (data, wh)

    def make_html(self, results):
        resp = []
        fh = file('head.html')
        data = fh.read()
        fh.close()
        resp.append(data)
        resp.append('<div style="margin-left: 20px">')

        resp.append("<div>URL Tested: %s</div><br/>" % results['url'])
        if results['okay']:
            resp.append(
                '<div><h2 style="color:green">Validated successfully</h2></div>')
        else:
            resp.append(
                '<div><h2 style="color:red">Validation Error: %s</h2></div>' %
                results['error'])

        if results.get('warnings', []):
            resp.append('<div style="margin-top: 20px">Warnings:<ul>')
            for w in results['warnings']:
                resp.append('<li>%s</li>' % w)
            resp.append('</ul></div>')

        resp.append('</div>')
        fh = file('foot.html')
        data = fh.read()
        fh.close()
        resp.append(data)

        return ''.join(resp)

    def format_response(self, data, fmt):
        if fmt == "html":
            response.content_type = "text/html"
            return self.make_html(data)
        else:
            response.content_type = "application/json"
            return json.dumps(data)

    def do_test(self):
        url = request.query.get('url', '')
        typ = request.query.get('type', 'manifest')
        version = request.query.get('version', '2.0')
        fmt = request.query.get('format', 'html')

        url = url.strip()
        try:
            (data, webhandle) = self.fetch(url)
        except:
            return self.format_response(
                {'okay': 0, 'error': 'Cannot fetch url', 'url': url}, fmt)

        # First check HTTP level
        ct = webhandle.headers.get('content-type', '')
        cors = webhandle.headers.get('access-control-allow-origin', '')

        warnings = []
        if not ct.startswith('application/json') and not ct.startswith(
                'application/ld+json'):
            # not json
            warnings.append(
                "URL does not have correct content-type header: got \"%s\", expected JSON" % ct)
        if cors != "*":
            warnings.append(
                "URL does not have correct access-control-allow-origin header: got \"%s\", expected *" % cors)

        # Now check data
        reader = ManifestReader(data, version=version)
        err = None
        try:
            mf = reader.read()
            js = mf.toJSON()
            # Passed!
            okay = 1
        except Exception, err:
            # Failed
            okay = 0

        warnings.extend(reader.get_warnings())
        infojson = {'url': url, 'okay': okay, 'warnings': warnings,
                    'error': str(err)}
        return self.format_response(infojson, fmt)

    def dispatch_views(self):
        self.app.route("/validate", "GET", self.do_test)

    def after_request(self):
        """A bottle hook for json responses."""
        # response["content_type"] = "application/json"
        methods = 'GET'
        headers = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = methods
        response.headers['Access-Control-Allow-Headers'] = headers
        response.headers['Allow'] = methods

    def not_implemented(self, *args, **kwargs):
        """Returns not implemented status."""
        abort(501)

    def empty_response(self, *args, **kwargs):
        """Empty response"""

    options_list = empty_response
    options_detail = empty_response

    def error(self, error, message=None):
        """Returns the error response."""
        return self._jsonify({"error": error.status_code,
                              "message": error.body or message}, "")

    def get_bottle_app(self):
        """Returns bottle instance"""
        self.app = Bottle()
        self.dispatch_views()
        self.app.hook('after_request')(self.after_request)
        return self.app


def apache():
    v = Validator();
    return v.get_bottle_app()


def main():
    v = Validator()
    run(host='localhost', port=8080, app=v.get_bottle_app())


if __name__ == "__main__":
    main()
else:
    application = apache()
