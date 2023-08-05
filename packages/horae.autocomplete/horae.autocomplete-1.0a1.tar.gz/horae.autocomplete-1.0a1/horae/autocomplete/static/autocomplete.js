var autocomplete = {
  listeners: []
};
(function($) {
  
  autocomplete.init = function(container) {
    container.find('input.autocomplete').each(function() {
      if($(this).data('autocomplete-initialized'))
        return;
      var name = $(this).attr('name');
      $(this).data('name', name.substr(0, name.length-7));
      $(this).attr('name', 'autocomplete');
      $(this).next('.button').remove();
      $(this).parents('.widget').addClass('autocomplete-widget');
      $(this).parents('.widget').find('label').addClass('autocomplete-value').removeClass('AutocompleteWidget').removeClass('AutocompleteChoiceWidget');
      $(this).autocomplete({
        source: $(this).attr('data'),
        focus: autocomplete.focus,
        select: autocomplete.select
      });
      $(this).data('autocomplete-initialized', true);
    });
  }
  
  autocomplete.focus = function(e, ui) {
    e.preventDefault();
  }
  
  autocomplete.select = function(e, ui) {
    var item = $(this).parent().find('input[name^="'+$(this).data('name')+'"][value="'+ui.item.value+'"]');
    if(item.size()) {
      if($(this).hasClass('AutocompleteChoiceWidget') || !item.is(':checked'))
        item.click();
    } else {
      item = $('<label class="autocomplete-value"> '+ui.item.label+'</label>');
      if($(this).hasClass('AutocompleteListWidget'))
        item.prepend('<input name="'+$(this).data('name')+':list" class="checkboxType" value="'+ui.item.value+'" type="checkbox" checked="checked" />');
      else
        item.prepend('<input name="'+$(this).data('name')+'" class="radioType" value="'+ui.item.value+'" type="radio" checked="checked" />');
      item.insertBefore($(this));
    }
    $(this).val('');
    e.preventDefault();
    for(var i=0; i<autocomplete.listeners.length; i++)
      autocomplete.listeners[i](item);
  }
  
  autocomplete.subscribe = function(listener) {
    autocomplete.listeners.push(listener);
  }
  
  $(document).ready(function() {
    autocomplete.init($(document));
  });
})(jQuery);
