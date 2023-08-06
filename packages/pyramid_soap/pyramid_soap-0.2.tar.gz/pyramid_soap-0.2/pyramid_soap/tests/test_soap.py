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
    hour = xsd.Element(xsd.String)


class GetAverageStockPrice(xsd.ComplexType):
    company = xsd.Element(xsd.String, minOccurs=1)
    week = xsd.Element(xsd.String)


class StockPrice(xsd.ComplexType):
    price = xsd.Element(xsd.Integer)


class AverageStockPrice(xsd.ComplexType):
    price = xsd.Element(xsd.Integer)


Schema = xsd.Schema(
    #Should be unique URL, can be any string.
    targetNamespace="http://127.0.0.1:8000/utsx/pid.xsd",
    #Register all complex types to schema.
    complexTypes=[GetStockPrice, GetAverageStockPrice,
                  AverageStockPrice, StockPrice],
    elements={
        "getStockPrice": xsd.Element(GetStockPrice),
        "getAverageStockPrice": xsd.Element(GetAverageStockPrice),
        "stockPrice": xsd.Element(StockPrice),
        "averageStockPrice": xsd.Element(AverageStockPrice),
    }
)


soap_hello = SOAPService(
    targetNamespace="http://127.0.0.1:8000/utsx/pid.wsdl",
    location="http://127.0.0.1:8000/utsx",
    path="/utsx",
    schema=Schema,
    version=SOAPVersion.SOAP11)


@soap_hello.api(soapAction="GetStockPrice",
                operationName="GetStockPrice",
                input="getStockPrice",
                output="stockPrice")
def get_stock_price(request, gsp):
    # print "=====>", gsp.hour, gsp.company
    return StockPrice(price=139)


@soap_hello.api(soapAction="GetAverageStockPrice",
                operationName="GetAverageStockPrice",
                input="getAverageStockPrice",
                output="averageStockPrice")
def get_average_stock_price(request, gsp):
    # print "=====>", gsp.week, gsp.company
    return AverageStockPrice(price=140)


headers1 = {
    'Soapaction': '"GetStockPrice"',
    'Content-Type': 'text/xml',
}

client_body1 = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://127.0.0.1:8000/utsx/pid.xsd"
    xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<ns1:Body>
<ns0:getStockPrice>
  <company>Google</company>
  <hour>2010-08-20T21:39:59</hour>
</ns0:getStockPrice>
</ns1:Body>
</SOAP-ENV:Envelope>
"""

headers2 = {
    'Soapaction': '"GetAverageStockPrice"',
    'Content-Type': 'text/xml',
}

client_body2 = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://127.0.0.1:8000/utsx/pid.xsd"
    xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<ns1:Body>
<ns0:getAverageStockPrice>
  <company>Google</company>
  <week>20</week>
</ns0:getAverageStockPrice>
</ns1:Body>
</SOAP-ENV:Envelope>
"""


class TestService(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.scan("pyramid_soap.tests.test_soap")
        self.app = TestApp(CatchErrors(self.config.make_wsgi_app()))

    def tearDown(self):
        testing.tearDown()

    def test_soap1(self):
        response = self.app.post('/utsx',
            headers=headers1,
            extra_environ=headers1,
            params=client_body1)
        #print response
        self.assertTrue('<price>139</price>' in response)

    def test_soap2(self):
        response = self.app.post('/utsx',
            headers=headers2,
            extra_environ=headers2,
            params=client_body2)
        #print response
        self.assertTrue('<price>140</price>' in response)
