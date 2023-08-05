import datetime
import decimal

from simplegeneric import generic
from mako.template import Template

from wsme.exc import ClientSideError
from wsme.api import pexpose
from wsme.protocols import CallContext
from wsme.utils import *
from wsme.types import iscomplex, list_attributes, Unset

try:
    import simplejson as json
except ImportError:
    import json

api_template = Template("""\
Ext.require('Ext.direct.*');

% for ns in sorted(namespaces):
Ext.define('${fullns(ns)}', {
    singleton: true,
    requires: ['Ext.direct.*'],

    Descriptor: {
        "url": "${webpath}/extdirect/router/${ns}",
        "namespace": "${fullns(ns)}",
        "type": "remoting",
        "actions": ${dumps(namespaces[ns], indent=4)},
        "enableBuffer": true
    }
}, function() {
  Ext.direct.Manager.addProvider(${fullns(ns)}.Descriptor);
});

% endfor
""")


@generic
def fromjson(datatype, value):
    if iscomplex(datatype):
        newvalue = datatype()
        for attrdef in list_attributes(datatype):
            if attrdef.key in value:
                setattr(newvalue, attrdef.key,
                        fromjson(attrdef.datatype, value[attrdef.key]))
        value = newvalue
    return value


@generic
def tojson(datatype, value):
    if value is None:
        return value
    if iscomplex(datatype):
        d = {}
        for attrdef in list_attributes(datatype):
            attrvalue = getattr(value, attrdef.key)
            if attrvalue is not Unset:
                d[attrdef.key] = tojson(attrdef.datatype, attrvalue)
        value = d
    return value


@fromjson.when_type(list)
def array_fromjson(datatype, value):
    return [fromjson(datatype[0], item) for item in value]


@tojson.when_type(list)
def array_tojson(datatype, value):
    if value is None:
        return value
    return [tojson(datatype[0], item) for item in value]


# datetime.time

@fromjson.when_object(datetime.time)
def time_fromjson(datatype, value):
    return parse_isotime(value)


@tojson.when_object(datetime.time)
def time_tojson(datatype, value):
    if value is None:
        return value
    return value.isoformat()


# datetime.date

@fromjson.when_object(datetime.date)
def date_fromjson(datatype, value):
    return parse_isodate(value)


@tojson.when_object(datetime.date)
def date_tojson(datatype, value):
    if value is None:
        return value
    return value.isoformat()


# datetime.datetime

@fromjson.when_object(datetime.datetime)
def datetime_fromjson(datatype, value):
    return parse_isodatetime(value)


@tojson.when_object(datetime.datetime)
def datetime_tojson(datatype, value):
    if value is None:
        return value
    return value.isoformat()


# decimal.Decimal

@fromjson.when_object(decimal.Decimal)
def decimal_fromjson(datatype, value):
    return decimal.Decimal(value)


@tojson.when_object(decimal.Decimal)
def decimal_tojson(datatype, value):
    if value is None:
        return value
    return str(value)


class ExtCallContext(CallContext):
    def __init__(self, request, namespace, calldata):
        super(ExtCallContext, self).__init__(request)
        self.namespace = namespace

        self.tid = calldata['tid']
        self.action = calldata['action']
        self.method = calldata['method']
        self.params = calldata['data']


class ExtDirectProtocol(object):
    """
    ExtDirect protocol.

    For more detail on the protocol, see
    http://www.sencha.com/products/extjs/extdirect.

    .. autoattribute:: name
    .. autoattribute:: content_types
    """
    name = 'extdirect'
    content_types = ['application/json', 'text/javascript']

    def __init__(self, namespace='', params_notation='named',
            nsfolder=None):
        self.namespace = namespace
        self.appns, self.apins = namespace.rsplit('.', 2)
        self.default_params_notation = params_notation
        self.appnsfolder = nsfolder

    @property
    def api_alias(self):
        if self.appnsfolder:
            alias = '%s/%s/%s.js' % (
                self.root._webpath, self.appnsfolder,
                self.apins.replace('.', '/'))
            return alias

    def accept(self, req):
        path = req.path
        assert path.startswith(self.root._webpath)
        path = path[len(self.root._webpath):]

        return path == self.api_alias or \
                     path == "/extdirect/api" or \
                     path.startswith("/extdirect/router")

    def iter_calls(self, req):
        path = req.path

        assert path.startswith(self.root._webpath)
        path = path[len(self.root._webpath):].strip()

        if path == self.api_alias or path.endswith('api'):
            req.wsme_extdirect_batchcall = False
            context = CallContext(req)
            context.path = ['_protocol', self.name, 'api']
            yield context
        else:
            assert path.startswith('/extdirect/router'), path
            path = path[17:].strip('/')

            if path:
                namespace = path.split('.')
            else:
                namespace = []

            data = json.loads(req.body)
            req.wsme_extdirect_batchcall = isinstance(data, list)
            if not req.wsme_extdirect_batchcall:
                data = [data]
            req.callcount = len(data)

            for call in data:
                yield ExtCallContext(req, namespace, call)

    def extract_path(self, context):
        path = list(context.namespace)

        if context.action:
            path.append(context.action)

        path.append(context.method)

        return path

    def read_arguments(self, context):
        funcdef = context.funcdef
        if funcdef.protocol_specific and funcdef.name == 'api':
            return {}
        notation = funcdef.extra_options.get(
                'extdirect_params_notation', self.default_params_notation)
        args = context.params
        if notation == 'positional':
            kw = dict((argdef.name, fromjson(argdef.datatype, arg))
                    for argdef, arg in zip(funcdef.arguments, args))
        elif notation == 'named':
            if len(args) == 0:
                args = [{}]
            elif len(args) > 1:
                raise ClientSideError(
                    "Named arguments: takes a single object argument")
            args = args[0]
            kw = dict( (argdef.name, fromjson(argdef.datatype, args[argdef.name]))
                for argdef in funcdef.arguments if argdef.name in args
            )
        else:
            raise ValueError("Invalid notation: %s" % notation)
        return kw

    def encode_result(self, context, result):
        return json.dumps({
            'type': 'rpc',
            'tid': context.tid,
            'action': context.action,
            'method': context.method,
            'result': tojson(context.funcdef.return_type, result)
        })

    def encode_error(self, context, infos):
        return json.dumps({
            'type': 'exception',
            'tid': context.tid,
            'action': context.action,
            'method': context.method,
            'message': '%(faultcode)s: %(faultstring)s' % infos,
            'where': infos['debuginfo']})

    def prepare_response_body(self, request, results):
        r = ",\n".join(results)
        if request.wsme_extdirect_batchcall:
            return "[\n%s\n]" % r
        else:
            return r

    def get_response_status(self, request):
        return 200

    def get_response_contenttype(self, request):
        return "text/javascript"

    def fullns(self, ns):
        return ns and '%s.%s' % (self.namespace, ns) or self.namespace

    @pexpose(contenttype="text/javascript")
    def api(self):
        namespaces = {}
        for path, funcdef in self.root.getapi():
            if len(path) > 1:
                namespace = '.'.join(path[:-2])
                action = path[-2]
            else:
                namespace = ''
                action = ''
            if namespace not in namespaces:
                namespaces[namespace] = {}
            if action not in namespaces[namespace]:
                namespaces[namespace][action] = []
            notation = funcdef.extra_options.get('extdirect_params_notation',
                self.default_params_notation)
            namespaces[namespace][action].append({
                'name': funcdef.name,
                'len': notation == 'named' and 1 or len(funcdef.arguments)})
        return api_template.render(
            namespaces=namespaces,
            webpath=self.root._webpath,
            rootns=self.namespace,
            fullns=self.fullns,
            dumps=json.dumps,
            )
