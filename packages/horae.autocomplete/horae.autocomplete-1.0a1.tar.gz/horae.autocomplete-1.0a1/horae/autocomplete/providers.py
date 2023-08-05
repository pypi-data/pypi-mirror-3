from simplejson import dumps

from zope import interface
from zope import component
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.formlib.interfaces import IFormField
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserPublisher, IBrowserRequest
from zope.security.checker import Checker, CheckerPublic, defineChecker

from horae.autocomplete import interfaces


def find_provider(context, request, field):
    provider = component.queryMultiAdapter((context, field, request), interfaces.IValueProvider, name=field.__name__)
    if provider is None:
        provider = component.queryMultiAdapter((field, request), interfaces.IValueProvider, name=field.__name__)
    if provider is None:
        provider = component.queryMultiAdapter((context, field, request), interfaces.IValueProvider)
    if provider is None:
        provider = component.queryMultiAdapter((field, request), interfaces.IValueProvider)
    return provider


class AbstractValueProvider(object):
    """ An abstract :py:class:`horae.autocomplete.interfaces.IValueProvider`
    """
    interface.implements(interfaces.IValueProvider)

    def __init__(self, field, request):
        self.field = field
        self.request = request

    def _searchVocabulary(self, value, vocabulary):
        values = []
        value = value.lower()
        for term in vocabulary:
            if ITitledTokenizedTerm.providedBy(term) and \
               term.title.lower().startswith(value):
                values.append((term.token, term.title))
                continue
            elif term.token.lower().startswith(value):
                values.append((term.token, term.title if ITitledTokenizedTerm.providedBy(term) else term.token))
        return values

    def __call__(self, term):
        """ Returns a list of value, title tuples matching the given value
        """
        raise NotImplementedError(
            "__call__(term) must be implemented by a subclass"
            )

    def browserDefault(self, request):
        return self, None


class AbstractContextValueProvider(AbstractValueProvider):
    """ An abstract context :py:class:`horae.autocomplete.interfaces.IValueProvider`
    """

    def __init__(self, context, field, request):
        super(AbstractContextValueProvider, self).__init__(field, request)
        self.context = context


class ChoiceValueProvider(AbstractContextValueProvider):
    """ A choice :py:class:`horae.autocomplete.interfaces.IValueProvider`
    """

    def __call__(self, term):
        """ Returns a list of value, title tuples matching the given value
        """
        field = self.field.bind(self.context)
        return self._searchVocabulary(term, field.vocabulary)


class ListValueProvider(AbstractContextValueProvider):
    """ A list :py:class:`horae.autocomplete.interfaces.IValueProvider`
    """

    def __call__(self, term):
        """ Returns a list of value, title tuples matching the given value
        """
        field = self.field.bind(self.context)
        return self._searchVocabulary(term, field.value_type.vocabulary)


class ProviderBrowserPublisher(object):
    component.adapts(interfaces.IValueProvider, IBrowserRequest)
    interface.implements(IBrowserPublisher)

    def __init__(self, provider, request):
        self.provider = provider
        self.request = request

    def __call__(self):
        return dumps([{'label': label, 'value': value} for value, label in self.provider(self.request.get('term', ''))])

    def browserDefault(self, request):
        return self, None

defineChecker(ProviderBrowserPublisher, Checker({'__call__': CheckerPublic}))


class ValuesTraverser(object):
    interface.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, form, ignored):
        field = None
        field_provider = component.queryMultiAdapter((self.context, self.request), interfaces.IFieldProvider)
        if field_provider is not None:
            field = field_provider(self.request.form.get('field'))
        if field is None:
            form = component.getMultiAdapter((self.context, self.request), name=form.replace('@', ''))
            field = form.form_fields.get(self.request.form.get('field'), None)
        if field is None:
            form()
            field = form.form_fields.get(self.request.form.get('field'), None)
            if field is None:
                return None
        if IFormField.providedBy(field):
            field = field.field
        provider = find_provider(self.context, self.request, field)
        return provider
