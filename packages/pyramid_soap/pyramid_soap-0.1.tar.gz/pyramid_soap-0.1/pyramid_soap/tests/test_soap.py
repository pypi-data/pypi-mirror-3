import unittest

from webtest import TestApp

from pyramid import testing
from pyramid.httpexceptions import HTTPException
from webob.dec import wsgify
from webob import exc

from pyramid_soap import SOAPService, SOAPVersion, xsd


class CatchErrors(object):
    def __init__(self, app):
        self.app = app
        if hasattr(app, 'registry'):
            self.registry = app.registry

    @wsgify
    def __call__(self, request):
        try:
            return request.get_response(self.app)
        except (exc.HTTPException, HTTPException), e:
            return e


#===============================================================
#                   Soap Service
#===============================================================


class GetStockPrice(xsd.ComplexType):
    company = xsd.Element(xsd.String, minOccurs=1)
    hora = xsd.Element(xsd.String)


class StockPrice(xsd.ComplexType):
    price = xsd.Element(xsd.Integer)


Schema = xsd.Schema(
    #Should be unique URL, can be any string.
    targetNamespace="http://127.0.0.1:8000/utsx/pid.xsd",
    #Register all complex types to schema.
    complexTypes=[GetStockPrice, StockPrice],
    elements={
        "getStockPrice": xsd.Element(GetStockPrice),
        "stockPrice": xsd.Element(StockPrice)
    }
)


soap_hello = SOAPService(
    targetNamespace="http://127.0.0.1:8000/utsx/pid.wsdl",
    location="http://127.0.0.1:8000/utsx",
    path="/utsx",
    schema=Schema,
    version=SOAPVersion.SOAP11)


@soap_hello.api(soapAction="GetStockPrice", input="getStockPrice",
                output="stockPrice", operationName="GetStockPrice")
def get_stock_price(request, gsp):
    return StockPrice(price=139)


client_body = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://127.0.0.1:8000/utsx/pid.xsd"
    xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<ns1:Body>
<ns0:getStockPrice>
  <company>Google</company>
  <hora>2010-08-20T21:39:59</hora>
</ns0:getStockPrice>
</ns1:Body>
</SOAP-ENV:Envelope>
"""

headers = {
    'Soapaction': '"GetStockPrice"',
    'Content-Type': 'text/xml',
}


class TestService(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.scan("pyramid_soap.tests.test_soap")
        self.app = TestApp(CatchErrors(self.config.make_wsgi_app()))

    def tearDown(self):
        testing.tearDown()

    def test_soap(self):
        response = self.app.post('/utsx',
            headers=headers,
            extra_environ=headers,
            params=client_body)
        #print response
        self.assertTrue('<price>139</price>' in response)
