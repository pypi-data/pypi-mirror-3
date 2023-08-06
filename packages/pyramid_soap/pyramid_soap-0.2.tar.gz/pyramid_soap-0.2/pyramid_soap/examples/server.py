""" Test of uts api.
"""

import logging

from pyramid.config import Configurator

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.wsgi.c_wsgi_server import GWSGIServer

from pyramid_soap import SOAPService, SOAPVersion, xsd


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


#===============================================================
#                   Pyramid application
#===============================================================
def get_application(**settings):
    config = Configurator(
        debug_logger=logging,
        settings=settings,
    )
    config.scan(".")
    return config.make_wsgi_app()


#===============================================================
#                   Server
#===============================================================
settings = {
    'debug_notfound': True,
    'debug_routematch': True,
}


class GPrincipal(GObj):
    """  Server Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, {})

    def start_up(self):
        self.wsgiserver = self.create_gobj(
            None,
            GWSGIServer,
            self,
            host='0.0.0.0',
            port=8000,
            application=get_application(**settings),
            trace_dump=False,
        )

        osettings = {
            'GObj.trace_mach': True,
            'GObj.logger': logging,
        }
        self.overwrite_parameters(-1, **osettings)


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    ga_srv = GAplic('ApiTest')
    ga_srv.create_gobj('principal', GPrincipal, None)

    try:
        ga_srv.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
