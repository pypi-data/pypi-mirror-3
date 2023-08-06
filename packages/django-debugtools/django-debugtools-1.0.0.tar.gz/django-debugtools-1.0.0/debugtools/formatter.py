"""
An enhanced ``pprint.pformat`` that prints data structures in a readable HTML style.
"""

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.forms.forms import BaseForm
from django.template import Node
from django.utils.encoding import smart_str
from django.utils.functional import Promise
from django.utils.html import escape
from itertools import chain
from pprint import pformat
import re
import inspect
import types


RE_SQL_NL = re.compile(r'\b(FROM|LEFT OUTER|RIGHT|LEFT|INNER|OUTER|WHERE|ORDER BY|GROUP BY)\b')
RE_SQL = re.compile(r'\b(SELECT|UPDATE|DELETE'
                    r'|COUNT|AVG|MAX|MIN|CASE'
                    r'|FROM|SET'
                    r'|ORDER|GROUP|BY|ASC|DESC'
                    r'|WHERE|AND|OR|IN|LIKE|BETWEEN|IS|NULL'
                    r'|LEFT|RIGHT|INNER|OUTER|JOIN|HAVING)\b')

def pformat_sql_html(sql):
    """
    Highlight common SQL words in a string.
    """
    sql = escape(sql)
    sql = RE_SQL_NL.sub(u'<br>\n\\1', sql)
    sql = RE_SQL.sub(u'<strong>\\1</strong>', sql)
    return sql


def pformat_django_context_html(object):
    """
    Dump a variable to a HTML string with sensible output for template context fields.
    It filters out all fields which are not usable in a template context.
    """
    if isinstance(object, QuerySet):
        return escape(serialize('python', object))
    elif isinstance(object, basestring):
        return escape(repr(object))
    elif isinstance(object, Promise):
        # lazy() object
        return escape(_format_lazy(object))
    else:
        if hasattr(object, '__dict__'):
            # Instead of just printing <SomeType at 0xfoobar>, expand the fields.
            # Construct a dictionary that will be passed to pformat()

            attrs = object.__dict__.iteritems()
            if object.__class__:
                # Add class members too.
                attrs = chain(attrs, object.__class__.__dict__.iteritems())

            # Remove private and protected variables
            # Filter needless exception classes which are added to each model.
            attrs = dict(
                (k, v)
                for k, v in attrs
                    if not k.startswith('_')
                    and not getattr(v, 'alters_data', False)
                    and not (isinstance(v, type) and issubclass(v, (ObjectDoesNotExist, MultipleObjectsReturned)))
            )

            # Add members which are not found in __dict__.
            # This includes values such as auto_id, c, errors in a form.
            for member in dir(object):
                if member.startswith('_') or not hasattr(object, member):
                    continue

                value = getattr(object, member)
                if callable(value) or attrs.has_key(member) or getattr(value, 'alters_data', False):
                    continue

                attrs[member] = value


            # Format property objects
            for name, value in attrs.items():  # not iteritems(), so can delete.
                if isinstance(value, property):
                    attrs[name] = _try_call(lambda: getattr(object, name))
                elif isinstance(value, types.FunctionType):
                    spec = inspect.getargspec(value)
                    if len(spec.args) != 1:
                        # should be simple method(self) signature to be callable in the template
                        del attrs[name]
                    else:
                        attrs[name] = _try_call(lambda: value(object))


            # Include representations which are relevant in template context.
            if getattr(object, '__str__', None) != object.__str__:
                attrs['__str__'] = _try_call(lambda: smart_str(object))
            if hasattr(object, '__iter__'):
                attrs['__iter__'] = LiteralStr('<iterator object>')
            if hasattr(object, '__getitem__'):
                attrs['__getitem__'] = LiteralStr('<dynamic item>')
            if hasattr(object, '__getattr__'):
                attrs['__getattr__'] = LiteralStr('<dynamic attribute>')

            # Add known __getattr__ members which are useful for template designers.
            if isinstance(object, BaseForm):
                for field_name in object.fields.keys():
                    attrs[field_name] = object[field_name]
                del attrs['__getitem__']


            _format_dict_values(attrs)
            object = attrs

        elif isinstance(object, dict):
            object = object.copy()
            _format_dict_values(object)

        elif isinstance(object, list):
            object = object[:]
            for i, value in enumerate(object):
                object[i] = _format_value(value)

        # Format it
        try:
            text = pformat(object)
        except Exception, e:
            return u"<caught %s while rendering: %s>" % (e.__class__.__name__, str(e) or "<no exception message>")

        return _style_text(text)


def pformat_dict_summary_html(dict):
    """
    Briefly print the dictionary keys.
    """
    return _style_text('{' + ',\n '.join("'{0}': ...".format(key) for key in sorted(dict.iterkeys())) + '}')


RE_PROXY = re.compile(escape(r'([\[ ])' + r'<django.utils.functional.__proxy__ object at 0x[0-9a-f]+>'))
RE_FUNCTION = re.compile(escape(r'([\[ ])' + r'<function [^ ]+ at 0x[0-9a-f]+>'))
RE_GENERATOR = re.compile(escape(r'([\[ ])' + r'<generator object [^ ]+ at 0x[0-9a-f]+>'))
RE_OBJECT_ADDRESS = re.compile(escape(r'([\[ ])' + r'<([^ ]+) object at 0x[0-9a-f]+>'))
RE_CLASS_REPR = re.compile(escape(r'([\[ ])' + r"<class '([^']+)'>"))
RE_FIELD_END = re.compile(escape(r",([\r\n] ')"))
RE_FIELDNAME = re.compile(escape(r"^ u?'([^']+)': "), re.MULTILINE)
RE_REQUEST_FIELDNAME = re.compile(escape(r"^(\w+):\{'([^']+)': "), re.MULTILINE)
RE_REQUEST_CLEANUP1 = re.compile(escape(r"\},([\r\n]META:)"))
RE_REQUEST_CLEANUP2 = re.compile(escape(r"\)\}>$"))


def _style_text(text):
    # Escape text and apply some formatting.
    # To have really good highlighting, pprint would have to be re-implemented.

    # Remove dictionary sign. that was just a trick for pprint
    if text == '{}':
        return '   <small>(<var>empty dict</var>)</small>'
    if text[0] == '{':  text = ' ' + text[1:]
    if text[-1] == '}': text = text[:-1]

    text = escape(text)
    text = text.replace(' &lt;iterator object&gt;', " <small>&lt;<var>this object can be used in a 'for' loop</var>&gt;</small>")
    text = text.replace(' &lt;dynamic item&gt;', ' <small>&lt;<var>this object may have extra field names</var>&gt;</small>')
    text = text.replace(' &lt;dynamic attribute&gt;', ' <small>&lt;<var>this object may have extra field names</var>&gt;</small>')
    text = RE_PROXY.sub('\g<1><small>&lt;<var>proxy object</var>&gt;</small>', text)
    text = RE_FUNCTION.sub('\g<1><small>&lt;<var>object method</var>&gt;</small>', text)
    text = RE_GENERATOR.sub("\g<1><small>&lt;<var>generator, use 'for' to traverse it</var>&gt;</small>", text)
    text = RE_OBJECT_ADDRESS.sub('\g<1><small>&lt;\g<2> object</var>&gt;</small>', text)
    text = RE_CLASS_REPR.sub('\g<1><small>&lt;\g<2> class</var>&gt;</small>', text)
    text = RE_FIELD_END.sub('\g<1>', text)
    text = RE_FIELDNAME.sub('   <strong style="color: #222;">\g<1></strong>: ', text)  # need 3 spaces indent to compensate for missing '..'

    # Since Django's WSGIRequest does a pprint like format for it's __repr__, make that styling consistent
    text = RE_REQUEST_FIELDNAME.sub('\g<1>:\n   <strong style="color: #222;">\g<2></strong>: ', text)
    text = RE_REQUEST_CLEANUP1.sub('\g<1>', text)
    text = RE_REQUEST_CLEANUP2.sub(')', text)

    return text


def _format_dict_values(attrs):
    # Format some values for better display
    for name, value in attrs.iteritems():
        attrs[name] = _format_value(value)


def _format_value(value):
    if isinstance(value, Node):
        # The Block node is very verbose, making debugging hard.
        return LiteralStr(u"<Block Node: {0}, ...>".format(value.name))
    elif isinstance(value, Promise):
        # lazy() object
        return _format_lazy(value)
    else:
        return value


def _format_lazy(value):
    args = value._proxy____args
    kw = value._proxy____kw
    if not kw and len(args) == 1 and isinstance(args[0], basestring):
        # Found one of the Xgettext_lazy() calls.
        return LiteralStr(u'ugettext_lazy({0})'.format(repr(value._proxy____args[0])))

    # Prints <django.functional.utils.__proxy__ object at ..>
    return value


def _try_call(func, extra_exceptions=()):
    try:
        return func()
    except (TypeError, KeyError, AttributeError, ObjectDoesNotExist) as e:
        return e
    except extra_exceptions as e:
        return e


class LiteralStr(object):
    """
    A trick to make pformat() print a custom string without quotes.
    """
    def __init__(self, rawvalue):
        self.rawvalue = rawvalue

    def __repr__(self):
        if isinstance(self.rawvalue, basestring):
            return self.rawvalue
        else:
            return repr(self.rawvalue)
