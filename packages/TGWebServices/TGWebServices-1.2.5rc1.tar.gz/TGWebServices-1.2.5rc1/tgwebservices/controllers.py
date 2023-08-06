# Web Services controllers
"""Handles the Controller part of MVC for web services. This provides the
WebServicesController class which is the main entry point for people wanting
to use web services."""

import logging
import types
import re
import sys
import traceback

import cherrypy
try:
#    # python 2.5 ?
    from xml.etree import cElementTree as et
except ImportError:
#    # python 2.4 ? so try to get stand-alone version
    import cElementTree as et

from genshi.builder import tag, Element

from turbogears import controllers, expose as tgexpose
from turbogears import config
from turbogears.decorator import weak_signature_decorator
from turbogears import validators

from tgwebservices import soap, iconv
from tgwebservices.runtime import register, primitives, \
                                  FunctionInfo, register_complex_type, \
                                  ctvalues

config.update({"tg.empty_flash": False})

log = logging.getLogger("tgwebservices.controller")


def dict_wrapped_result(func):
    """Wraps a call to a function so that the return value is put into a
    single item dictionary, with the key 'result'.

    :param func: Function to wrap
    :return: a new function
    """
    def d_w_r(*args, **kw):
        return dict(result=func(*args, **kw))
    return d_w_r

_wrong_parameters = re.compile(r".*\(\) takes .* \(\d+ given\)")
_unexpected_parameters = re.compile(r".*\(\) got an unexpected keyword "
                                    "argument .*")


def wsexpose(return_type=basestring):
    """Exposes a method for access via web services. Only one value
    can be returned because many languages only support a single
    return value from methods.

    :param return_type: the class that will be returned. This is used to
                        help statically typed clients."""
    def entangle(func):
        fi = register(func)
        fi.return_type = return_type

        # we'll use the TurboGears version of expose to handle JSON
        # output.
        tgfunc = dict_wrapped_result(func)
        tgfunc = tgexpose(
            "wsautojson", accept_format="text/javascript",
            content_type="application/json",
            tg_format='json')(tgfunc)
        tgfunc = tgexpose(
            "wsautojson", accept_format="application/json",
            content_type="application/json",
            tg_format='json')(tgfunc)
        tgfunc = tgexpose(
            "wsautoxml", accept_format="text/xml",
            content_type='text/xml',
            )(tgfunc)

        def newfunc(self, **kw):
            jsonp = None
            if "tg_format" in kw:
                if kw["tg_format"] == "json":
                    cherrypy.request.headers["Accept"] = "text/javascript"
                    # Intercept jsonp parameter if passed along.
                    if 'jsonp' in kw:
                        jsonp = kw.pop("jsonp")
                else:
                    cherrypy.request.headers["Accept"] = "text/xml"
                del kw["tg_format"]

            request = cherrypy.request
            input_types = fi.input_types

            # the _tgws keyword is used when a web service system, such as
            # SOAP, is calling the function rather than a call that is being
            # made via direct URL traversal.
            if "_tgws" in kw:
                webservice = True
                del kw["_tgws"]
            else:
                webservice = False

            if "xml_body" in kw:
                kw = iconv.handle_xml_params(kw["xml_body"], input_types)
            elif "_xml_request" in kw:
                try:
                    data = kw["_xml_request"]
                    body = et.fromstring(data)
                except SyntaxError:
                    raise validators.Invalid("Request XML is invalid", "",
                                             None)
                kw = iconv.handle_xml_params(body, input_types)
            elif "_json_request" in kw:
                kw = iconv.handle_json_params(kw["_json_request"], input_types)
            elif request.headers.get("Content-Type", "") \
                 .startswith("text/xml"):
                try:
                    clen = int(request.headers.get('Content-Length')) or 0
                    data = request.body.read(clen)
                    body = et.fromstring(data)
                except SyntaxError:
                    raise validators.Invalid("Request XML is invalid", "",
                                             None)
                kw = iconv.handle_xml_params(body, input_types)
            elif request.headers.get("Content-Type", "") \
                .startswith("application/json"):
                clen = int(request.headers.get('Content-Length')) or 0
                data = request.body.read(clen)
                kw = iconv.handle_json_params(data, input_types)
            else:
                iconv.handle_keyword_params(kw, input_types)

            try:
                if webservice:
                    return func(self, **kw)
                else:
                    # when direct traversal is used, call the standard
                    # TurboGears expose mechanism.
                    request._tgws_call = True
                    outp = tgfunc(self, **kw)
                    del request._tgws_call
                    if jsonp:
                        outp = jsonp + "(" + outp + ");"
                    return outp
            except TypeError:
                # handle the case where a bogus parameter was sent in to the
                # function
                msg = str(sys.exc_info()[1])
                if (_unexpected_parameters.match(msg) or
                    _wrong_parameters.match(msg)) and \
                    msg.startswith(func.__name__):
                    raise validators.Invalid(
                        "Unexpected parameter in function call (%s)" % msg,
                        None, None)
                else:
                    raise

        newfunc.exposed = True
        newfunc.__name__ = func.__name__
        newfunc.__doc__ = func.__doc__
        newfunc._ws_func_info = fi
        # a list denotes that the user is returning an array of the type
        # given by the first element in the array
        # we need to keep track of the complex types so that they can be
        # defined as appropriate for the given protocol
        if isinstance(return_type, list):
            rt = return_type[0]
            if rt not in primitives:
                register_complex_type(fi, rt)
        elif return_type not in primitives:
            register_complex_type(fi, return_type)

        return newfunc
    return entangle


def wsvalidate(*args, **kw):
    """Validates and converts incoming parameters. Also registers the
    parameters used by the method for use by statically typed languages.
    Method parameters can be specified via positional or keyword arguments.
    You should pass in the class used for each parameter."""
    def entangle(func):
        fi = register(func)
        input_types = dict()

        # match up the validators with the function parameters

        # the validators list doesn't include self, but the parameters list
        # does. So, the parameters list is offset by one higher.
        for i in range(0, len(args)):
            argtype = args[i]
            input_types[fi.params[i]] = argtype

        input_types.update(kw)

        # Make sure all of the input types are registered
        # so they show up in the WSDL.
        for argname, argtype in input_types.items():
            if isinstance(argtype, list):
                typetoreg = argtype[0]
            else:
                typetoreg = argtype
            if typetoreg not in primitives:
                log.info('registering complex type %s for %s',
                         typetoreg, argname)
                register_complex_type(fi, typetoreg)

        fi.input_types = input_types
        return func
    return entangle


class WebServicesController(object):
    """A controller that implements a piece of a web services API."""

    def _ws_gather_functions_and_types(self, prefix):
        """Collects all of the functions and types on this controller and the
        controllers beneath it."""
        funcs = dict()
        complex_types = set()
        for key in dir(self):
            if key.startswith("_"):
                continue
            item = getattr(self, key)

            # functions are globally registered with Java-style
            # camelCase names
            if prefix:
                newname = prefix + key[0].upper() + key[1:]
            else:
                newname = key

            # check for functions and sub-controllers
            if isinstance(item, types.MethodType) and \
                    hasattr(item, "_ws_func_info"):
                funcs[newname] = item
                complex_types.update(item._ws_func_info.complex_types)
            elif hasattr(item, "_ws_gather_functions_and_types"):
                morefuncs, moretypes = \
                            item._ws_gather_functions_and_types(newname)
                funcs.update(morefuncs)
                complex_types.update(moretypes)
        return funcs, complex_types


class WebServicesRoot(WebServicesController):
    """The root of a multi-protocol web service.

    :param baseURL: Sets the URL path for this controller (trailing '/'
                    included). Some protocols need to know this.
    :param tns: The SOAP target namespace (defaults to baseURL+soap/)
    :param typenamespace: the namespace for the SOAP types (defaults to
                          baseURL+soap/types)
    """

    def __init__(self, baseURL, tns=None, typenamespace=None):
        """Constructor for a WebServicesRoot controller.
        """

        if not tns:
            tns = baseURL + "soap/"
        if not typenamespace:
            typenamespace = tns + "types"
        self._ws_baseURL = baseURL
        self._ws_parent = None
        self.soap = soap.SoapController(self, tns, typenamespace)
        self._ws_funcs, self._ws_complex_types = \
            self._ws_gather_functions_and_types("")

    def _cp_on_error(self):
        excinfo = sys.exc_info()
        cherrypy.response.body = self._formatexception(excinfo)

    @tgexpose("wsautoxml", allow_json=True, accept_format="text/xml")
    def _formatexception(self, excinfo):
        if isinstance(excinfo[1], validators.Invalid):
            return dict(faultcode="Client",
                        faultstring=str(excinfo[1]))
        else:
            return dict(faultcode="Server",
                        faultstring=str(excinfo[1]),
                        debuginfo="\nTraceback:\n%s\n" %
                            "\n".join(traceback.format_exception(
                                                    *excinfo)))
