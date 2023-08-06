"""Tests for HTTP+XML services"""

import cStringIO as StringIO

import cherrypy
from turbogears import testutil
import base64
import decimal

try:
    # python >= 2.5
    from xml.etree import cElementTree as et
except ImportError:
    import cElementTree as et

from tgwebservices.tests.fixtures import *

def test_simple():
    cherrypy.root = MyService("http://foo.bar.baz")
    testutil.create_request("/times2?value=5")
    print cherrypy.response.headers["Content-Type"]
    assert cherrypy.response.headers["Content-Type"] == "text/xml; charset=utf-8"
    output = cherrypy.response.body[0]
    print output
    assert output == """<result>10</result>"""

def test_xml_error():
    testutil.create_request("/times2?value=5&foo=1")
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><faultcode>Client</faultcode><faultstring>foo is not a valid parameter (valid values are: ['value'])</faultstring></result>"""

def test_complex_input():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    request = """<request>
    <person><name>Fred</name><age>22</age></person>
</request>"""
    testutil.create_request("/tenyearsolder", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "text/xml; charset=utf-8"})
    print cherrypy.response.headers["Content-Type"]
    assert cherrypy.response.headers["Content-Type"] == "text/xml; charset=utf-8"
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                     """<name>Fred</name></result>"""

def test_complex_input_on_get():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    request = """<request><person><name>Fred</name><age>22</age></person></request>"""
    testutil.create_request("/tenyearsolder?tg_format=xml&_xml_request=%s" % request)
    print cherrypy.response.headers["Content-Type"]
    assert cherrypy.response.headers["Content-Type"] == "text/xml; charset=utf-8"
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                     """<name>Fred</name></result>"""


def test_complex_params():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    person = """<person><name>Fred</name><age>22</age></person>
"""
    testutil.create_request("/tenyearsolder?tg_format=xml&person=%s" % person)
    print cherrypy.response.headers["Content-Type"]
    assert cherrypy.response.headers["Content-Type"] == "text/xml; charset=utf-8"
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><age>32</age><computed>Hello!</computed>""" \
                     """<name>Fred</name></result>"""


def test_rwproperty():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    request = """<request>
    <rwp><value>AValue</value></rwp>
</request>"""
    testutil.create_request("/getandsetrwprop", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "text/xml; charset=utf-8"})
    print cherrypy.response.headers["Content-Type"]
    assert cherrypy.response.headers["Content-Type"] == "text/xml; charset=utf-8"
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><value>AValue</value></result>"""

def test_datetime():
    cherrypy.root = DateTimeService("http://foo.bar.baz/")
    request = """<request><d>2009-07-25</d><t>22:14:53.89654242</t></request>"""
    testutil.create_request("/combine?tg_format=xml&_xml_request=%s" % request)
    output = cherrypy.response.body[0]
    print output

    assert output == '<result>2009-07-25T22:14:53.896542</result>'

    request = """<request><dt>2009-07-25T22:14:53.89654242</dt></request>"""
    testutil.create_request("/split?tg_format=xml&_xml_request=%s" % request)
    output = cherrypy.response.body[0]
    print output

    assert output == '<result><d>2009-07-25</d><t>22:14:53.896542</t></result>'

def test_binary():
    data = '\xc2\xc3\xc4'

    cherrypy.root = BinaryService("http://foo.bar.baz/")
    request = "<request><data>%s</data></request>" % base64.encodestring(data)
    print request

    testutil.create_request("/reverse", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "text/xml; charset=utf-8"})
    output = cherrypy.response.body[0]

    print output

    r = et.fromstring(output)
    rdata = base64.decodestring(r.text)

    assert data == rdata[::-1]

def test_null():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    
    request = """<request><rwp><value nil="true"/></rwp></request>"""
    testutil.create_request("/getandsetrwprop", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "text/xml; charset=utf-8",
                                     "Accept" : 
                                        "text/xml"})
    output = cherrypy.response.body[0]
    print output
    assert output == """<result><value nil="true"/></result>"""

def test_decimal():
    cherrypy.root = DecimalService("http://foo.bar.baz/")

    request = """<request><d>7.325</d><quanta>0.01</quanta></request>"""

    testutil.create_request("/quantize", rfile=StringIO.StringIO(request),
                            method="POST",
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" :
                                       "text/xml; charset=utf-8",
                                     "Accept" :
                                       "text/xml"})
    output = cherrypy.response.body[0]

    print output
    assert output == """<result>7.32</result>"""


