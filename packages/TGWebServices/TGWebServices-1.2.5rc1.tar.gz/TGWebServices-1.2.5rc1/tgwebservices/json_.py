from simplejson import JSONEncoder
import datetime
import decimal

from tgwebservices.runtime import ctvalues, binary
from turbojson import jsonify


class TGWSJSON(jsonify.GenericJSON):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.time, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, binary):
            return obj.base64()
        return super(TGWSJSON, self).default(obj)

_encoder = TGWSJSON()


class AutoJSONTemplate(object):
    def __init__(self, extra_vars_func=None, options=None):
        pass

    def load_template(self, templatename):
        "There are no actual templates with this engine"
        pass

    def render(self, info, format="json", fragment=False, template=None):
        "Renders the template to a string using the provided info."
        if "result" not in info:
            info = dict(result=info)
        out = _encoder.encode(dict(result=info.get('result')))
        return out

    def get_content_type(self, user_agent):
        return "application/json"
