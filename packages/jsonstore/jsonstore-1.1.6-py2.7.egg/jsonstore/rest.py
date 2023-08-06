import re
from urllib import unquote
from urlparse import urljoin
from datetime import datetime
from hashlib import sha1
import operator

from webob import Request, Response
from simplejson import loads, dumps, JSONEncoder

from jsonstore.store import EntryManager, ConflictError
from jsonstore import rison
from jsonstore import operators


def make_app(global_conf, **kwargs):
    return JSONStore(**kwargs)


class DatetimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat().split('.', 1)[0] + 'Z'


class JSONStore(object):
    def __init__(self, *args, **kwargs):
        """
        A REST(ish) interface to the JSON store.

        """
        self.em = EntryManager(*args, **kwargs)

    def __call__(self, environ, start_response):
        req = Request(environ)
        method = req.GET.get('method') or req.method
        func = getattr(self, method)
        res = func(req)
        return res(environ, start_response)

    def GET(self, req):
        path_info = req.path_info.lstrip('/') or '{}'  # empty search
        tokens = [ load_entry(unquote(token)) for token in path_info.split('/') ]

        # first token is either an id or a search dict
        obj = tokens.pop(0)
        if isinstance(obj, dict):
            obj = replace_operators(obj)
            x_items = self.em.search(obj, count=True)
            result = self.em.search(obj, req.GET.get('size'), req.GET.get('offset'))
        else:
            try:
                result = self.em.search(__id__=obj)[0]
                result = reduce(operator.getitem, [result] + tokens)
                x_items = 1
            except (IndexError, KeyError):
                return Response(status='404 Not Found')

        body = dumps(result, cls=DatetimeEncoder, indent=4)
        etag = '"%s"' % sha1(body).hexdigest()
        if etag in req.if_none_match:
            return Response(status='304 Not Modified')

        jsonp = req.GET.get('jsonp') or req.GET.get('callback')
        if jsonp:
            body = jsonp + '(' + body + ')'
            content_type = 'text/javascript'
        else:
            content_type = 'application/json'

        return Response(
                body=body,
                content_type=content_type,
                charset='utf8',
                headerlist=[('X-ITEMS', str(x_items)), ('etag', etag)])

    def HEAD(self, req):
        response = self.GET(req)
        response.body = ''
        return response

    def POST(self, req):
        entry = load_entry(req.body)
        try:
            result = self.em.create(entry)
        except ConflictError:
            return Response(status='409 Conflict')
        body = dumps(result, cls=DatetimeEncoder, indent=4)
        etag = '"%s"' % sha1(body).hexdigest()
        location = urljoin(req.application_url, result['__id__'])

        return Response(
                status='201 Created',
                body=body,
                content_type='application/json',
                charset='utf8',
                headerlist=[('Location', location), ('etag', etag)])

    def PUT(self, req):
        entry = load_entry(req.body)
        url_id = req.path_info.lstrip('/')
        if '__id__' not in entry:
            entry['__id__'] = url_id
        elif url_id != entry['__id__']:
            return Response(status='409 Conflict')

        # Conditional PUT. This is useful for implementing counters, eg.
        def condition(old):
            etag = '%s' % sha1(dumps(old, cls=DatetimeEncoder, indent=4)).hexdigest()  # no quotes to check against req.if_match
            return etag in req.if_match or (
                    req.if_unmodified_since and 
                    req.if_unmodified_since >= old['__updated__'])
        try:
            result = self.em.update(entry, condition)
        except ConflictError:
            return Response(status='412 Precondition Failed')

        body = dumps(result, cls=DatetimeEncoder, indent=4)
        etag = '"%s"' % sha1(body).hexdigest()

        return Response(
                body=body,
                content_type='application/json',
                charset='utf8',
                headerlist=[('etag', etag)])
        
    def DELETE(self, req):
        id_ = req.path_info.lstrip('/')
        self.em.delete(id_)

        return Response(
                status='204 No Content',
                body='',
                content_type='application/json',
                charset='utf8')


def load_entry(s):
    try:
        entry = loads(s)
    except ValueError:
        try:
            entry = rison.loads(s)
        except (ValueError, rison.ParserException):
            entry = s
    return entry


def replace_operators(obj):
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = replace_operators(v)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                obj[k][i] = parse_op(item)
        else:
            obj[k] = parse_op(v)
    return obj


def parse_op(obj):
    if not isinstance(obj, basestring):
        return obj

    for op in operators.__all__:
        m = re.match(op + r'\((.*?)\)', obj)
        if m:
            operator = getattr(operators, op)
            args = m.group(1)
            args = loads('[' + args + ']')
            return operator(*args)
    return obj


if __name__ == '__main__':
    from paste.httpserver import serve
    app = JSONStore('test.db')
    serve(app, port=8081)
