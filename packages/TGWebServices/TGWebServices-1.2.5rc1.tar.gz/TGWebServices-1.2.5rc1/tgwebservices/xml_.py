"""A template plugin that generates simple XML"""
from genshi.builder import Element

from peak.rules import abstract, when

from tgwebservices.runtime import primitives, ctvalues, typedproperty, binary
from datetime import datetime, date, time
import decimal

_simplevalues = set([int, long, float, bool])
_strvalues = set([basestring, str, unicode])
_datetimevalues = set([datetime, date, time])


@abstract()
def xml_value(name, value):
    """Converts a value into XML Element objects."""
    pass


@when(xml_value, "type(value) in _strvalues")
def xml_string(name, value):
    elem = Element(name)
    elem(value)
    return elem


@when(xml_value, "type(value) in _datetimevalues")
def xml_datetime(name, value):
    elem = Element(name)
    elem(value.isoformat())
    return elem


@when(xml_value, "type(value) in _simplevalues")
def xml_simple(name, value):
    elem = Element(name)
    elem(str(value))
    return elem


@when(xml_value, "type(value) == binary")
def xml_binary(name, value):
    elem = Element(name)
    elem(value.base64())
    return elem


@when(xml_value, "type(value) == decimal.Decimal")
def xml_decimal(name, value):
    elem = Element(name)
    elem(str(value))
    return elem

@when(xml_value, "value is None")
def xml_none(name, value):
    elem = Element(name, nil='true')
    return elem


@when(xml_value, "value is not None and type(value) not in primitives")
def xml_instance(name, value):
    """Handles an instance of a complex type."""
    elem = Element(name)
    cls = value.__class__
    for key in ctvalues(cls):
        elem.append(xml_value(key, getattr(value, key)))
    return elem


@when(xml_value, "isinstance(value, list)")
def xml_list(name, value):
    elem = Element(name)
    for item in value:
        elem.append(xml_value("item", item))
    return elem


@when(xml_value, "isinstance(value, dict)")
def xml_dict(name, value):
    elem = Element(name)
    for key in value.keys():
        if key.startswith("tg_"):
            continue
        elem.append(xml_value(key, value[key]))
    return elem


class AutoXMLTemplate(object):

    def __init__(self, extra_vars_func=None, options=None):
        pass

    def load_template(self, templatename):
        "There are no actual templates with this engine"
        pass

    def render(self, info, format="xml", fragment=False, template=None):
        "Renders the template to a string using the provided info."
        if "result" not in info:
            info = dict(result=info)
        return str(xml_value("result", info["result"]))

    def get_content_type(self, user_agent):
        return "text/xml"
