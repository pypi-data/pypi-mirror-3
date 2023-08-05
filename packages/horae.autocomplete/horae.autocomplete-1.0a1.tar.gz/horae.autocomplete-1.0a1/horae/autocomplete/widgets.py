from zope import interface
from zope.i18n import translate
from zope.schema import vocabulary
from zope.formlib.itemswidgets import RadioWidget, MultiCheckBoxWidget
from zope.formlib.widget import renderElement
from zope.i18nmessageid import MessageFactory

_z = MessageFactory('zope')

from horae.autocomplete import resource
from horae.autocomplete import interfaces
from horae.autocomplete.providers import find_provider


class AbstractAutocompleteWidget(object):
    """ An abstract autocomplete widget
    """
    interface.implements(interfaces.IAutocompleteWidget)

    form_url = None

    def __call__(self):
        resource.css.need()
        resource.js.need()
        if self.form_url is None:
            self.form_url = self.request.getURL()
        self.search_results = []
        if '%s.dosearch' % self.name in self.request.form and \
           self.request.form.get('%s.search' % self.name, None) is not None:
            provider = find_provider(self.context.context, self.request, self.context)
            if provider is not None:
                self.search_results = dict(provider(self.request.form.get('%s.search' % self.name))).keys()
        return super(AbstractAutocompleteWidget, self).__call__()

    def autocompleteInput(self):
        parts = self.form_url.split('/')
        return renderElement('input',
                             data='%s/++values++%s?field=%s' % ('/'.join(parts[:-1]), parts[-1], self.name[len(self._prefix):],),
                             type='text',
                             cssClass='autocomplete %s' % self.cssClass,
                             name='%s.search' % self.name,
                             value=u'') + ' ' + \
               renderElement('input',
                             type='submit',
                             cssClass='button',
                             name='%s.dosearch' % self.name,
                             value=translate(_z(u'search-button', default=u'Search'), context=self.request))

    def renderItemsWithValues(self, values):
        """ Only render selected values or contained in the search_results
        """
        cssClass = self.cssClass
        rendered_items = []
        count = 0
        for value in values:
            if not value in self.vocabulary:
                continue
            term = self.vocabulary.getTerm(value)
            rendered_items.append(self.renderSelectedItem(count,
                self.textForValue(term),
                term.token,
                self.name,
                cssClass))
            count += 1

        for value in self.search_results:
            if value in values or not value in self.vocabulary:
                continue
            term = self.vocabulary.getTerm(value)
            rendered_items.append(self.renderItem(count,
                self.textForValue(term),
                term.token,
                self.name,
                cssClass))
            count += 1
        return rendered_items + [self.autocompleteInput(), ]


class AutocompleteChoiceWidget(AbstractAutocompleteWidget, RadioWidget):
    """ An autocomplete choice widget
    """
    cssClass = 'AutocompleteWidget AutocompleteChoiceWidget'
    orientation = 'vertical'
    _displayItemForMissingValue = False


class AutocompleteListChoiceWidget(AbstractAutocompleteWidget, MultiCheckBoxWidget):
    """ An autocomplete list choice widget
    """
    cssClass = 'AutocompleteWidget AutocompleteListWidget'
    orientation = 'vertical'


class AutocompleteListSequenceWidget(AutocompleteListChoiceWidget):
    """ An autocomplete list sequence widget
    """

    def renderItemsWithValues(self, values):
        self.vocabulary = vocabulary.SimpleVocabulary.fromValues(values + self.search_results)
        return super(AutocompleteListSequenceWidget, self).renderItemsWithValues(values)

    def convertTokensToValues(self, tokens):
        return tokens
