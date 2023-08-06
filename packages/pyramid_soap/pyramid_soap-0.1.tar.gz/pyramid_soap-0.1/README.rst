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

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
