import base64
import datetime
import decimal

from simplegeneric import generic
from mako.template import Template

from wsme.exc import ClientSideError
from wsme.controller import pexpose, CallContext
from wsme.utils import *
from wsme.types import iscomplex, list_attributes, binary

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
        "actions": ${dumps(namespaces[ns], indent=4)}
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
        for name, attrdef in list_attributes(datatype):
            setattr(newvalue, name,
                fromjson(attrdef.datatype, value[name]))
        value = newvalue
    return value


@generic
def tojson(datatype, value):
    if iscomplex(datatype):
        d = {}
        for name, attrdef in list_attributes(datatype):
            d[name] = tojson(attrdef.datatype, getattr(value, name))
        value = d
    return value


@fromjson.when_type(list)
def array_fromjson(datatype, value):
    return [fromjson(datatype[0], item) for item in value]


@tojson.when_type(list)
def array_tojson(datatype, value):
    return [tojson(datatype[0], item) for item in value]


# datetime.time

@fromjson.when_object(datetime.time)
def time_fromjson(datatype, value):
    return parse_isotime(value)


@tojson.when_object(datetime.time)
def time_tojson(datatype, value):
    return value.isoformat()


# datetime.date

@fromjson.when_object(datetime.date)
def date_fromjson(datatype, value):
    return parse_isodate(value)


@tojson.when_object(datetime.date)
def date_tojson(datatype, value):
    return value.isoformat()


# datetime.datetime

@fromjson.when_object(datetime.datetime)
def datetime_fromjson(datatype, value):
    return parse_isodatetime(value)


@tojson.when_object(datetime.datetime)
def datetime_tojson(datatype, value):
    return value.isoformat()


# decimal.Decimal

@fromjson.when_object(decimal.Decimal)
def decimal_fromjson(datatype, value):
    return decimal.Decimal(value)


@tojson.when_object(decimal.Decimal)
def decimal_tojson(datatype, value):
    return str(value)


@fromjson.when_object(binary)
def binary_fromjson(datatype, value):
    return base64.decodestring(value)


@tojson.when_object(binary)
def binary_tojson(datatype, value):
    return base64.encodestring(value)


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
        yield CallContext(req)

    def extract_path(self, context):
        req = context.request
        path = req.path
        assert path.startswith(self.root._webpath)
        path = path[len(self.root._webpath):].strip()

        if path == self.api_alias or path.endswith('api'):
            return ['_protocol', self.name, 'api']

        assert path.startswith('/extdirect/router'), path
        path = path[17:].strip('/')

        if path:
            path = path.split('.')
        else:
            path = []

        # TODO check it extAction is set, which means a form post
        data = json.loads(req.body)
        if isinstance(data, list) and len(data) != 1:
            raise ClientSideError(
                "This ExtDirect does not support batch calls")
        else:
            data = [data]

        action = data[0]['action']
        if action:
            path.append(action)
        method = data[0]['method']
        path.append(method)

        context.extdirect_data = data

        return path

    def read_arguments(self, context):
        funcdef = context.funcdef
        if funcdef.protocol_specific and funcdef.name == 'api':
            return {}
        notation = funcdef.extra_options.get(
                'extdirect_params_notation', self.default_params_notation)
        args = context.extdirect_data[0]['data']
        if notation == 'positional':
            kw = dict((argdef.name, fromjson(argdef.datatype, arg))
                    for argdef, arg in zip(funcdef.arguments, args))
        elif notation == 'named':
            if len(args) == 0:
                args = {}
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
            'tid': context.extdirect_data[0]['tid'],
            'action': '',
            'method': '',
            'result': tojson(context.funcdef.return_type, result)
        })

    def encode_error(self, context, infos):
        return json.dumps({
            'type': 'exception',
            'message': '%(faultcode)s: %(faultstring)s' % infos,
            'where': infos['debuginfo']})

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
