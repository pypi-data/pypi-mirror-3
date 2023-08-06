""" Test of uts api.
"""

from pprint import pprint
import logging

from pyramid.config import Configurator

log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)


from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_wsgi_server import GWSGIServer

from pyramid_soap import SOAPService, SOAPVersion, xsd

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
    print gsp.company
    print gsp.hora
    return StockPrice(price=139)


#===============================================================
#                   Pyramid application
#===============================================================

def get_application(**settings):
    config = Configurator(
        debug_logger=log,
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
        self.set_trace_mach(True, pprint, level=-1)


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
