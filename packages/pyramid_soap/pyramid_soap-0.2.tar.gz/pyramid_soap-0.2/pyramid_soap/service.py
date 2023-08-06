"""
This module adapts Soapbox package to pyramid framework.
"""

import venusian
import functools
from lxml import etree

from soapbox.soap import SOAPVersion
from soapbox.utils import uncapitalize
from soapbox import py2wsdl, xsd

from pyramid.response import Response

_SOAP_ARGS = ('function', 'soapAction', 'input', 'location',
              'output', 'operationName', 'methods')
SOAP_HTTP_Transport = 'http://schemas.xmlsoap.org/soap/http'


class SOAPService(object):
    """Represents a service.
    Describes service aggregating informations required for dispatching and
    WSDL generation.

    Options can be passed to a service.

    :param name: the name of the service. Should be unique.

    :param path: the path the service is available at. Should also be unique.

    :param targetNamespace: #WSDL targetNamespace.

    :param schema: xsd.Schema instance.

    :param version: SOAP version. Can be SOAPVersion.SOAP11 or
    SOAPVersion.SOAP12. Default is SOAPVersion.SOAP11.

    :param factory: A factory returning callables that return true or false,
                    function of the given request. Exclusive with the 'acl'
                    option.

    :param acl: a callable that define the ACL (returns true or false, function
                of the given request. Exclusive with the 'factory' option.

    """

    def __init__(self, **kw):
        self.methods = []
        self.name = kw.pop('name', 'SOAP-Service')
        self.route_pattern = kw.pop('path')
        self.route_name = self.route_pattern
        self.location = kw.pop('location')  # to pass to soapbox
        self.targetNamespace = kw.pop('targetNamespace')
        self.schema = kw.pop('schema')

        self.renderer = kw.pop('renderer', 'soap')
        self.version = kw.pop('version', SOAPVersion.SOAP11)
        self.factory = kw.pop('factory', None)
        self.acl_factory = kw.pop('acl', None)

        if self.factory and self.acl_factory:
            raise ValueError("Cannot specify both 'acl' and 'factory'")
        self.kw = kw
        # to keep the order in which the services have been defined
        self.index = -1
        self.definitions = {}

    def __repr__(self):
        return "<SOAP Service at %s>" % (self.route_name)

    def _make_route_factory(self):
        acl_factory = self.acl_factory

        class ACLResource(object):
            def __init__(self, request):
                self.request = request
                self.__acl__ = acl_factory(request)

        return ACLResource

    #
    # Aliases for the three most common verbs
    #
    # the actual decorator
    def api(self, **kw):
        api_kw = self.kw.copy()
        api_kw.update(kw)

        if 'renderer' not in api_kw:
            api_kw['renderer'] = self.renderer

        def _api(func):
            _api_kw = api_kw.copy()
            self._api_kw = _api_kw.copy()

            def callback(context, method_name, ob):
                """ context: pyramid config scan
                    method_name: str name of function
                    ob: function object
                """
                # Add action
                method = xsd.Method(
                    function=ob,
                    soapAction=_api_kw['soapAction'],
                    input=_api_kw['input'],
                    output=_api_kw['output'],
                    operationName=_api_kw['operationName'])
                self.methods.append(method)

                config = context.config.with_package(info.module)

                # setup the services hash if it isn't already
                services = config.registry.setdefault('soap_services', {})
                if self.index == -1:
                    self.index = len(services)

                # define the route (and view) if it isn't already
                if self.route_pattern not in services:
                    services[self.route_pattern] = self
                    route_kw = {}
                    if self.factory is not None:
                        route_kw["factory"] = self.factory
                    elif self.acl_factory is not None:
                        route_kw["factory"] = self._make_route_factory()
                    config.add_route(self.route_name, self.route_pattern, **route_kw)

                    view_kw = _api_kw.copy()
                    for arg in _SOAP_ARGS:
                        view_kw.pop(arg, None)

                    # method decorators
                    if 'attr' in view_kw:
                        @functools.wraps(getattr(ob, kw['attr']))
                        def view(request):
                            meth = getattr(ob(request), kw['attr'])
                            return meth()

                        del view_kw['attr']
                        view = functools.partial(call_service, view, self._api_kw)
                    else:
                        view = functools.partial(call_service, ob, self._api_kw)

                    # set the module of the partial function
                    setattr(view, '__module__', getattr(ob, '__module__'))

                    config.add_view(view=view,
                                    route_name=self.route_name, **view_kw)

            info = venusian.attach(func, callback, category='pyramid')

            if info.scope == 'class':
                # if the decorator was attached to a method in a class, or
                # otherwise executed at class scope, we need to set an
                # 'attr' into the settings if one isn't already in there
                if 'attr' not in kw:
                    kw['attr'] = func.__name__

            kw['_info'] = info.codeinfo   # fbo "action_method"

            return func
        return _api


def call_the_method(service, request, message, soap_action):
    '''
    '''
    for method in service.methods:
        if soap_action != method.soapAction:
            continue

        if isinstance(method.input, basestring):
            element = service.schema.elements[method.input]
            input_object = element._type.parsexml(message, service.schema)
        else:
            input_object = method.input.parsexml(message, service.schema)
        return_object = method.function(request, input_object)
        try:
            tagname = uncapitalize(return_object.__class__.__name__)
            return_object.xml(tagname, namespace=service.schema.targetNamespace,
                        elementFormDefault=service.schema.elementFormDefault,
                        schema=service.schema)  # Validation.
        except Exception, e:
            raise ValueError(e)

        if isinstance(method.output, basestring):
            tagname = method.output
        else:
            tagname = uncapitalize(return_object.__class__.__name__)
        return tagname, return_object
    raise ValueError('Method not found!')


def call_service(func, api_kwargs, context, request):
    """Wraps the request and the response, once a route does match."""
    pattern = request.matched_route.pattern
    service = request.registry['soap_services'].get(pattern)
    request.META = request.headers.environ  # to be used by soapbox, like django
    request.service = service

    SOAP = service.version

    if request.method == 'GET' and 'wsdl' in request.params:
        tree = py2wsdl.generate_wsdl(request.service)
        body = etree.tostring(tree, pretty_print=True)
        return Response(body=body, content_type=SOAP.CONTENT_TYPE)

    try:
        xml = request.body
        envelope = SOAP.Envelope.parsexml(xml)
        message = envelope.Body.content()
        soap_action = SOAP.determin_soap_action(request)
        tagname, return_object = call_the_method(service,
                                                 request, message, soap_action)
        soap_message = SOAP.Envelope.response(tagname, return_object)
        return Response(body=soap_message, content_type=SOAP.CONTENT_TYPE)
    except (ValueError, etree.XMLSyntaxError) as e:
        response = SOAP.get_error_response(SOAP.Code.CLIENT, str(e))
    except Exception, e:
        response = SOAP.get_error_response(SOAP.Code.SERVER, str(e))
    return Response(body=response, content_type=SOAP.CONTENT_TYPE)
