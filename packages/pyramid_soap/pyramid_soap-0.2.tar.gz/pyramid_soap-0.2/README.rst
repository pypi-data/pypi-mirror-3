pyramid_soap
============

The **pyramid_soap** package adapts
`Soapbox <http://packages.python.org/Soapbox/index.html>`_
for pyramid framework, to build SOAP Web Services.

Source code at `<https://bitbucket.org/artgins/pyramid_soap>`_

Example
=======

::

    from pyramid_soap import SOAPService, SOAPVersion, xsd

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


License
=======
pyramid_soap is released under terms of The MIT
License `MIT <http://www.opensource.org/licenses/mit-license>`_.

Copyright (c) 2012, Ginés Martínez Sánchez <ginsmar@artgins.com>

