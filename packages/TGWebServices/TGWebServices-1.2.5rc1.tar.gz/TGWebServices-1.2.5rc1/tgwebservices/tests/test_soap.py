import re
import httplib
import cStringIO as StringIO
import mimetools

import base64

from turbogears import testutil, validate
import cherrypy
try:
    # python >= 2.5
    from xml.etree import cElementTree as et
except ImportError:
    import cElementTree as et

from tgwebservices.controllers import WebServicesRoot, WebServicesController, \
                                      wsexpose, wsvalidate
from tgwebservices import soap
from tgwebservices.tests.fixtures import *
from tgwebservices import runtime

def run_soap(method, params=""):
    request = """<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">

  <soap:Body xmlns="http://foo.bar.baz/soap/">
    <%(method)s>
        %(params)s
    </%(method)s>
  </soap:Body>

</soap:Envelope>
""" % dict(method=method, params=params)

    print request
    testutil.create_request("/soap/", rfile=StringIO.StringIO(request), 
                            method="POST", 
                            headers={"Content-Length" : str(len(request)),
                                     "Content-Type" : 
                                        "application/soap+xml; charset=utf-8"})
    output = cherrypy.response.body[0]
    return output

def get_wsdl():
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print output
    return output

def test_basic_call():
    cherrypy.root = MyService("http://foo.bar.baz/")
    
    output = run_soap("times2", "<value>5</value>")
    print output
    root = et.fromstring(output)
    result_elements = list(root.findall(".//{http://foo.bar.baz/soap/types}result"))
    assert len(result_elements) == 1, "Should only have one result"
    elem = result_elements[0]
    print "result:", elem
    assert elem.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] == \
        "xsd:int", "Expected result to be labeled an int"
    assert elem.text == "10", "Expected result to be 10"

def test_wsdl_with_ints():
    cherrypy.root = MyService("http://foo.bar.baz/")

    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print output
    print cherrypy.response.headers["Content-Type"]
    assert cherrypy.response.headers["Content-Type"] == "text/xml; charset=utf-8"
    root = et.fromstring(output)
    schema_elements = root.findall(".//{http://www.w3.org/2001/XMLSchema}element")
    found = False
    for elem in schema_elements:
        print "FE:", elem
        if "name" in elem.attrib and elem.attrib["name"] == "times2Response":
            found = True
            interior_elem = elem[0][0][0]
            print "response value: %s (%s)" % (interior_elem, 
                                               interior_elem.attrib)
            assert elem[0][0][0].attrib["type"] == "xsd:int"
    assert found, "Should have found a definition for times2Response"

def test_wsdl_with_complex():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print output
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}element")
    found = False
    for elem in schema_elements:
        if "name" in elem.attrib and elem.attrib["name"] == \
                "getfancyResponse":
            found = True
            interior_elem = elem[0][0][0]
            print "response value: %s (%s)" % (interior_elem, 
                                               interior_elem.attrib)
            assert elem[0][0][0].attrib["type"] == "types:FancyValue"
    
    complex_types = root.findall(
                        ".//{http://www.w3.org/2001/XMLSchema}complexType")
    assert found, "Should have found a definition for fancyResponse"
    
    found = False
    found_array = False
    for elem in complex_types:
        if "name" in elem.attrib and elem.attrib["name"] == \
                        "FancyValue":
            found = True
            objattributes = elem[0].getchildren()
            found_name = False
            found_age = False
            found_computed = False
            for attr in objattributes:
                if attr.attrib["name"] == "name":
                    assert attr.attrib["type"] == "xsd:string"
                    found_name = True
                elif attr.attrib["name"] == "age":
                    assert attr.attrib["type"] == "xsd:int"
                    found_age = True
                elif attr.attrib["name"] == "computed":
                    assert attr.attrib["type"] == "xsd:string"
                    found_computed = True
                else:
                    assert False, "Found a %s element which shouldn't "\
                            "be there" % (attr.attrib["name"])
            assert found_name, "Did not find name element"
            assert found_age, "Did not find age element"
            assert found_computed, "Did not find computed element"
        elif "name" in elem.attrib and elem.attrib["name"] == \
            "FoodItem_Array":
            found_array = True
    assert found, "Should have found a delcaration for FancyValue"
    assert found_array, "Should have found the FoodItem_Array"

def test_soap_array():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print output
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
    found = False
    stringarray_found = False
    for elem in schema_elements:
        if "name" in elem.attrib and elem.attrib["name"] == \
                "FancyValue_Array":
            found = True
            interior_elem = elem[0]
            assert interior_elem.tag == \
                "{http://www.w3.org/2001/XMLSchema}sequence", \
                "Expected to find a sequence in FancyValue_Array"
            interior_elem = interior_elem[0]
            assert interior_elem.tag == \
                "{http://www.w3.org/2001/XMLSchema}element", \
                "Expected to find element in FancyValue_Array"
            print interior_elem.attrib
            assert interior_elem.attrib["maxOccurs"] == \
                "unbounded", "expected unbounded array"
            assert interior_elem.attrib["nillable"] == \
                "true", "Array should be nillable"
            assert interior_elem.attrib["type"] == \
                "types:FancyValue", \
                "Should have found array type declaration of FancyValue"
        if "name" in elem.attrib and elem.attrib["name"] == \
                "String_Array":
            stringarray_found = True
            interior_elem = elem[0][0]
            assert interior_elem.tag == \
                "{http://www.w3.org/2001/XMLSchema}element", \
                "Expected to find element in String_Array"
            print interior_elem.attrib
            assert interior_elem.attrib["type"] == \
                "xsd:string", \
                "Should have found string type for String_Array"
    
    assert found, "Expected to find the FancyValiue_Array type"
    assert stringarray_found, "Expected to find the String_Array type"
    
    output = run_soap("somestrings")
    root = et.fromstring(output)
    print "SOAP somestrings call output:", output
    result_elements = list(root.findall(".//{http://foo.bar.baz/soap/types}result"))
    assert len(result_elements) == 1
    items = result_elements[0].getchildren()
    assert len(items) == 3, "Expected three items in the array"
    assert items[0].text == "A"
    assert items[1].text == "B"
    assert items[2].text == "C"

def test_nested_complex():
    cherrypy.root = ComplexService("http://foo.bar.baz/")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
    found = False
    for elem in schema_elements:
        if "name" in elem.attrib and elem.attrib["name"] == "FoodOrder":
            found = True
            elements = elem.getchildren()[0].getchildren()
            assert len(elements) == 2
            foundarray = False
            for e in elements:
                if e.attrib["type"] == "types:FoodItem_Array":
                    foundarray = True
            assert foundarray, "Should have found array of FoodItems"
    assert found, "Should have found FoodOrder type"
    output = run_soap("getorder")
    print "\n\nSOAP:\n\n"
    print output
    assert '<item xsi:type="FoodItem">' in output
    root = et.fromstring(output)
    persontags = root.findall(".//{http://foo.bar.baz/soap/types}person")
    assert len(persontags) > 0
    assert FoodItem._type_dependents == 1

class LocalObject(object):
    name = ""

class LocalController(WebServicesRoot):
    @wsexpose(LocalObject)
    def getobj(self):
        return LocalObject()

def test_complex_types_stay_in_one_controller():
    cherrypy.root = LocalController("http://foo.bar.baz")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
    for elem in schema_elements:
        assert not ("name" in elem.attrib and elem.attrib["name"] == "FoodOrder"), \
            "Complex type definitions should be limited to controllers that use them"

def test_nested_controllers():
    cherrypy.root = OuterService("http://foo.bar.baz")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
    found = False
    for elem in schema_elements:
        if "name" in elem.attrib and elem.attrib["name"] == \
                        "FancyValue":
            found = True
    assert found, "Should have found FancyValue from the nested controller"
    operations = set(["ultimatequestion", "innerGetFancy", "innerFooGetFancy",
                      "anotherGetFancy"])
    porttype = root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType")[0]
    op_elements = porttype.findall(
                          ".//{http://schemas.xmlsoap.org/wsdl/}operation")
    for elem in op_elements:
        name = elem.attrib["name"]
        assert name in operations, "Found unexpected op %s in WSDL" % (name)
        operations.remove(name)
    assert not operations, "Did not find these ops: %s" % (operations)
    
def test_call_to_nested_controller():
    cherrypy.root = OuterService("http://foo.bar.baz")
    output = run_soap("innerFooGetFancy")
    print output
    assert """<innerFooGetFancyResponse><result xsi:type="FancyValue"><age xsi:type="xsd:int">42</age><computed xsi:type="xsd:string">Hello!</computed><name xsi:type="xsd:string">Mr. Bean</name></result></innerFooGetFancyResponse>""" in output

def test_documentation_strings():
    cherrypy.root = MyService("http://foo.bar.baz")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    root = et.fromstring(output)
    porttype = root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType")[0]
    operation = porttype.getchildren()[0]
    assert operation.attrib["name"] == "sum"
    docelems = operation.findall(
                ".//{http://schemas.xmlsoap.org/wsdl/}documentation")
    assert len(docelems) == 1
    assert docelems[0].text == "Sum all the values"

def test_fault_for_invalid_input():
    cherrypy.root = MyService("http://foo.bar.baz")
    output = run_soap("times2", """<value>whaleblubber</value>""")
    print cherrypy.response.status
    print output
    assert cherrypy.response.status == "500 Invalid Input"
    assert output == """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/"><Body><Fault><faultcode>Client</faultcode><faultstring>whaleblubber value for the 'value' parameter is not a valid int</faultstring></Fault></Body></Envelope>"""

def test_fault_for_exception():
    cherrypy.root = MyService("http://foo.bar.baz")
    output = run_soap("twentyover", """<value>0</value>""")
    print cherrypy.response.status
    assert cherrypy.response.status == "500 Internal Server Error"
    print output
    assert "SOAP method: twentyover" in output
    assert "foo.bar.baz/soap/" in output, "Raw request should be in the fault"
    assert "return 20 / value" in output, "Traceback should be in fault"
    assert "ZeroDivisionError" in output, "error should be in fault"

def test_boolean_type():
    elem = soap.soap_value("test", bool, True)
    output = str(elem)
    print output
    assert output == '<test xsi:type="xsd:boolean">true</test>'

def test_big_number():
    elem = soap.soap_value("test", int, 3063485326L)
    output = str(elem)
    assert output == '<test xsi:type="xsd:int">3063485326</test>'

def test_empty_list():
    cherrypy.root = ComplexService("http://foo.bar.baz")
    output = run_soap("getempty")
    print output
    assert "fault" not in output
    assert '<result xsi:type="FancyValue_Array"/>' in output

def test_too_many_arguments():
    output = run_soap("somestrings", "<bogus>value</bogus>")
    print output
    root = et.fromstring(output)
    fc = root.findall(".//{http://schemas.xmlsoap.org/soap/envelope/}faultcode")
    assert len(fc) == 1
    fc = fc[0]
    print "Fault code: ", fc.text
    assert fc.text == "Client"

def test_bogus_function_gives_client_fault():
    output = run_soap("nonexistentfunction")
    print output
    root = et.fromstring(output)
    fc = root.findall(".//{http://schemas.xmlsoap.org/soap/envelope/}faultcode")
    assert len(fc) == 1
    fc = fc[0]
    print "Fault code: ", fc.text
    assert fc.text == "Client"

def test_subclass_complex_types_should_appear_in_wsdl():
    output = get_wsdl()
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
    foundperson = False
    for elem in schema_elements:
        if "name" in elem.attrib and elem.attrib["name"] == "SubFood":
            for child in elem.getchildren()[0].getchildren():
                if child.attrib["name"] == "person":
                    foundperson = True
                    print "SubFood person type is %s" % child.attrib["type"]
                    assert child.attrib["type"] == "types:FancyValue", \
                              "SubFood person should be a FancyValue"
    assert foundperson, "Should have found the person attribute on SubFood"

def test_unsigned_integer():
    output = get_wsdl()
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}complexType")
    founditem = False
    for elem in schema_elements:
        if "name" in elem.attrib and elem.attrib["name"] == "FoodItem":
            for child in elem.getchildren()[0].getchildren():
                if child.attrib["name"] == "quantity":
                    founditem = True
                    print "FoodItem quantity type is %s" % child.attrib["type"]
                    assert child.attrib["type"] == "xsd:unsignedInt"
    assert founditem, "Should have found FoodItem's quantity field"
    elem = soap.soap_value("quantity", runtime.unsigned, 5)
    assert str(elem) == '<quantity xsi:type="xsd:unsignedInt">5</quantity>'

class NamespacedRoot(WebServicesRoot):
    @wsexpose(str)
    def world(self):
        return "Hello!"

def test_explicit_namespace():
    cherrypy.root = NamespacedRoot("https://foo.bar.baz/", 
        "http://foo.bar/service/URI/")
    output = get_wsdl()
    print output
    assert 'targetNamespace="http://foo.bar/service/URI/"' in output
    assert 'xmlns:types="http://foo.bar/service/URI/types"' in output

class OptionalParams(WebServicesRoot):
    @wsexpose(int)
    @wsvalidate(int, int, int)
    def addem(self, num1, num2=2, num3=3):
        return num1+num2+num3

def test_optional():
    cherrypy.root = OptionalParams("https://foo.bar.baz")
    output = get_wsdl()
    print output
    root = et.fromstring(output)
    schema_elements = root.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}element")
    for elem in schema_elements:
        if elem.attrib.get("name", None) == "addem":
            complextype = elem.getchildren()[0]
            sequence = complextype.getchildren()[0]
            num1 = sequence.getchildren()[0]
            assert num1.attrib["name"] == "num1"
            assert "minOccurs" not in num1.attrib
            num2 = sequence.getchildren()[1]
            assert num2.attrib["name"] == "num2"
            assert num2.attrib["minOccurs"] == "0"
            num3 = sequence.getchildren()[2]
            assert num3.attrib["name"] == "num3"
            assert num3.attrib["minOccurs"] == "0"

class StringRoot(WebServicesRoot):
    @wsexpose(str)
    @wsvalidate(str)
    def say_hello(self, name):
        assert name is not None
        assert name != "None"
        return "Hi, %s" % name

def test_empty_parameter_is_empty_string():
    cherrypy.root = StringRoot("http://foo.bar.baz/")
    output = run_soap("say_hello", """<name></name>""")
    print output
    assert "fault" not in output

class Person(object):
    name = str
    age = int

class ComplexInput(WebServicesRoot):
    @wsexpose()
    @wsvalidate(Person)
    def savePerson(self, p):
        self.person = p
    
def test_complex_input_simple_object():
    ci = ComplexInput("http://foo.bar.baz/")
    cherrypy.root = ci
    output = run_soap("savePerson", """<p>
    <name>George</name>
    <age>280</age>
</p>""")
    print output
    assert isinstance(ci.person, Person)

def test_rw_typedproperty():
    ci = ComplexService("http://foo.bar.baz/")
    cherrypy.root = ci
    output = run_soap("getandsetrwprop", """<rwp>
    <value>AValue</value>
</rwp>""")
    print output
    assert '<getandsetrwpropResponse><result xsi:type="ReadWriteProperty"><value xsi:type="xsd:string">AValue</value></result></getandsetrwpropResponse>' in output


def test_datetime():
    cherrypy.root = DateTimeService("http://foo.bar.baz/")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    assert "xsd:dateTime" in output

    output = run_soap("combine", "<d>2009-07-25</d><t>22:14:53.89654242</t>")
    print output

    assert """<combineResponse><result xsi:type="xsd:dateTime">2009-07-25T22:14:53.896542</result></combineResponse>""" in output

    output = run_soap("split", "<dt>2009-07-25T22:14:53.896542</dt>")
    print output
    assert """<splitResponse><result xsi:type="DateTimeStruct"><d xsi:type="xsd:date">2009-07-25</d><t xsi:type="xsd:time">22:14:53.896542</t></result></splitResponse>""" in output

def test_binary():
    cherrypy.root = BinaryService("http://foo.bar.baz/")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    assert "xsd:base64Binary" in output

    data = '\xc2\xc3\xc4'

    output = run_soap("reverse", "<data>%s</data>" % base64.encodestring(data))
    print output
    
    root = et.fromstring(output)
    r = root.find(".//{http://foo.bar.baz/soap/types}result")
    rdata = base64.decodestring(r.text)

    assert data == rdata[::-1]

def test_null():
    ci = ComplexService("http://foo.bar.baz/")
    cherrypy.root = ci
    output = run_soap("getandsetrwprop", """<rwp>
    <value xsi:nil="true"/>
</rwp>""")
    print output
    assert '<getandsetrwpropResponse><result xsi:type="ReadWriteProperty"><value xsi:nil="true"/></result></getandsetrwpropResponse>' in output

def test_decimal():
    cherrypy.root = DecimalService("http://foo.bar.baz/")
    testutil.create_request("/soap/api.wsdl")
    output = cherrypy.response.body[0]
    print "WSDL:\n\n"
    print output
    assert "xsd:decimal" in output

    output = run_soap("quantize", "<d>7.325</d><quanta>0.01</quanta>")
    print output
    
    root = et.fromstring(output)
    r = root.find(".//{http://foo.bar.baz/soap/types}result")
    assert r.text == '7.32'

