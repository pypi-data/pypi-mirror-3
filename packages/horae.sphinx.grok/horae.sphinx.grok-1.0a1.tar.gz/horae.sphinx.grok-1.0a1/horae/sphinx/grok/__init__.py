import types
from sphinx.util import force_decode
from sphinx.domains.python import PyClasslike, PyModulelevel
from sphinx.ext import autodoc


def value_converter(value):
    if isinstance(value, list) or isinstance(value, tuple):
        return ', '.join([value_converter(v) for v in value])
    if isinstance(value, types.ClassType) or isinstance(value, types.ObjectType):
        try:
            return ':py:class:`' + value.__module__ + '.' + value.__name__ + '`'
        except:
            pass
    return str(value)


class GrokDesc(PyClasslike):
    def get_signature_prefix(self, sig):
        return ''


class GrokDocumenter(autodoc.ClassDocumenter):
    """
    Specialized Documenter directive for grok components.
    """
    objtype = "grok"
    # Must be a higher priority than ClassDocumenter
    member_order = 10

    def __init__(self, *args, **kwargs):
        super(GrokDocumenter, self).__init__(*args, **kwargs)
        self.options.show_inheritance = True

    def get_doc(self, encoding=None):
        doc = super(GrokDocumenter, self).get_doc(encoding)
        docstrings = []
        for name, value in self.object.__dict__.items():
            if not name.startswith('grokcore'):
                continue
            docstrings.append(':' + name.split('.')[-1] + ':')
            docstrings.append('    ' + value_converter(value))
        if '__implemented__' in self.object.__dict__:
            if len(self.object.__implemented__.declared):
                docstrings.append(':implements:')
                docstrings.append('    ' + value_converter(self.object.__implemented__.declared))
        if not len(doc):
            doc.append([])
        return [doc[0] + [force_decode(docstring, encoding) for docstring in docstrings]]


class GrokFunctionDesc(PyModulelevel):
    def get_signature_prefix(self, sig):
        return ''


class GrokFunctionDocumenter(autodoc.FunctionDocumenter):
    """
    Specialized Documenter directive for functions using grok decorators
    """
    objtype = 'grokfunction'
    member_order = 40

    def get_doc(self, encoding=None):
        doc = super(GrokFunctionDocumenter, self).get_doc(encoding)
        docstrings = []
        for name, value in self.object.__dict__.items():
            if not name.startswith('__component_'):
                continue
            docstrings.append(':' + name.split('_')[3] + ':')
            docstrings.append('    ' + value_converter(value))
        if '__implemented__' in self.object.__dict__:
            ifaces = [iface for iface in self.object.__implemented__.interfaces()]
            if len(ifaces):
                docstrings.append(':implements:')
                docstrings.append('    ' + value_converter(ifaces))
        if not len(doc):
            doc.append([])
        return [doc[0] + [force_decode(docstring, encoding) for docstring in docstrings]]


try:
    from plone.memoize import volatile, instance

    def volatile_cache(get_key, get_cache=volatile.store_on_self):
        def decorator(fun):
            return fun
        return decorator
    volatile.cache = volatile_cache

    def instance_memoize(func):
        return func
    instance.memoize = instance_memoize

except ImportError:
    pass # plone.memoize not available


def setup(app):
    app.add_directive_to_domain('py', 'grok', GrokDesc)
    app.add_directive_to_domain('py', 'grokfunction', GrokFunctionDesc)
    app.add_autodocumenter(GrokDocumenter)
    app.add_autodocumenter(GrokFunctionDocumenter)
