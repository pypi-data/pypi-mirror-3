from zope import interface
from zope import schema
from zope.schema.interfaces import ITextLine, IChoice

from horae.autocomplete import interfaces


class AutocompleteList(schema.List):
    """ An autocomplete list field
    """
    interface.implements(interfaces.IAutocompleteList)

    def __init__(self, **kw):
        super(AutocompleteList, self).__init__(**kw)
        # whine if value_type is not a textline or choice field
        value_type = kw.get('value_type', None)
        if value_type is not None and not ITextLine.providedBy(value_type) and not IChoice.providedBy(value_type):
            raise ValueError("'value_type' must be TextLine or Choice field.")


class AutocompleteChoice(schema.Choice):
    """ An autocomplete choice field
    """
    interface.implements(interfaces.IAutocompleteChoice)
