# Release information about TGWebServices

version = "1.2.5rc1"

description = "Multiprotocol Web Services for TurboGears 1.x"
long_description = """TurboGears gives you a plain HTTP with JSON return
values API for your application for free. This isn't always what you want,
though. Sometimes, you don't want to expose all of the data to the web
that you need to render your templates. Maybe you need to support a
protocol that names the function it's calling as part of what it POSTs
such as SOAP or XML-RPC.

TGWebServices provides a super simple API for creating web services that
are available via SOAP, HTTP->XML, and HTTP->JSON. The SOAP API generates
WSDL automatically for your Python and even generates enough type
information for statically typed languages (Java and C#, for example) to
generate good client code on their end.

How easy is it?

::

    class Multiplier(WebServicesRoot):

        @wsexpose(int)
        @wsvalidate(int, int)
        def multiply(self, num1, num2):
            return num1 * num2

With this at the root, SOAP clients can find the WSDL file at /soap/api.wsdl
and POST SOAP requests to /soap/. HTTP requests to /multiply?num1=5&num2=20
will return an XML document with the result of 100. Add ?tg_format=json (or
an HTTP Accept: text/javascript header) and you'll get JSON back.

The great thing about this is that the code above looks like a '''normal
Python function''' and doesn't know a thing about web services.

A more complete documentation can be found at
http://wiki.tgws.googlecode.com/hg/index.html.

Features
--------

* Easiest way to expose a web services API
* Supports SOAP, HTTP+XML, HTTP+JSON
* Outputs wrapped document/literal SOAP, which is the most widely
  compatible format
* Provides enough type information for statically typed languages
  to generate conveniently usable interfaces
* Can output instances of your own classes
* Can also accept instances of your classes as input
* Works with TurboGears 1.0 and 1.1
* MIT license allows for unrestricted use"""
author = "Kevin Dangoor, Christophe de Vienne"
email = "turbogears-web-services@googlegroups.com"
copyright = "Copyright 2006, 2007 Kevin Dangoor, Arbor Networks." + \
            "2008-2012 The TGWebServices development team."

url = "http://code.google.com/p/tgws/"
license = "MIT"
