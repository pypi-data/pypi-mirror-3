from zope import interface
from zope.schema.interfaces import IList, IChoice


class IValueProvider(interface.Interface):
    """ Value providers are multi-adapters for field and request or context, field and request
    """

    def __call__(term):
        """ Returns a list of value, title tuples matching the given term
        """


class IAutocompleteField(interface.Interface):
    """ Autocomplete field
    """


class IAutocompleteList(IAutocompleteField, IList):
    """ Autocomplete list field
    """


class IAutocompleteChoice(IAutocompleteField, IChoice):
    """ Autocomplete choice field
    """


class IAutocompleteWidget(interface.Interface):
    """ Autocomplete widget
    """

    form_url = interface.Attribute("The URL of the form this widget belongs to")
    """ The URL of the form this widget belongs to
    """


class IFieldProvider(interface.Interface):
    """ Field providers are multi-adapters for object and request
    """

    def __call__(name):
        """ Returns a field
        """
