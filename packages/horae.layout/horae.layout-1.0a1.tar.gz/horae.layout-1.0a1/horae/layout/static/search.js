var search = {
  
  current_search: false
  
};
(function($) {
  
  search.blur = function() {
    if(!$(this).val())
      $(this).val($(this).attr('alt'));
    $(this).parents('form').find('.results').stop().fadeOut('fast');
  }
  search.focus = function() {
    if($(this).val() == $(this).attr('alt'))
      $(this).val('');
    var results = $(this).parents('form').find('.results');
    if(results.size())
      results.stop().fadeIn('fast');
    else
      $.proxy(search.changed, this)();
  }
  search.changed = function(e) {
    if(e && e.keyCode && (e.keyCode == 40 || e.keyCode == 38 || e.keyCode == 27 || e.keyCode == 13 || e.keyCode == 39 || e.keyCode == 37))
      return;
    var url = $(this).closest('form').attr('action').replace('search', 'livesearch');
    $(this).addClass('ui-autocomplete-loading');
    search.current_search = $.post(url, $(this).closest('form').serializeArray(), function(data, status, jqXHR) {
      if(jqXHR != search.current_search)
        return;
      $('#header .search-form form input[name="form.text"]').removeClass('ui-autocomplete-loading');
      var form = $('#header .search-form form');
      form.find('.results').remove();
      var results = $('<div class="results" />');
      if(data.results && data.results.length > 0) {
        $('#header .search-form li input').unbind('keydown', search.keyDown).keydown(search.keyDown);
        var list = $('<ul />');
        for(var i=0, l=data.results.length; i<l; i++)
          list.append('<li><a href="'+data.results[i]['url']+'"><small class="id">#'+data.results[i]['id']+'</small>'+data.results[i]['name']+'<span>'+data.results[i]['type']+'</span></a></li>');
        results.append(list);
      }
      if(data.message)
        results.append(data.message);
      if(results.html())
        form.append(results);
      results.show();
    }, 'json').error(function() {
      $('#header .search-form form input[name="form.text"]').removeClass('ui-autocomplete-loading');
    });
  }
  search.keyDown = function(e) {
    switch(e.keyCode) {
      case 40:
        e.preventDefault();
        search.next();
        break;
      case 38:
        e.preventDefault();
        search.previous();
        break;
      case 27:
        e.preventDefault();
        $('#header .search-form li input').blur();
        break;
      case 13:
        var current = search.current();
        if(current.size()) {
          e.preventDefault();
          document.location = current.find('a').attr('href');
        }
        break;
    }
  }
  search.current = function() {
    return $('#header .search-form form .results .current');
  }
  search.next = function() {
    var current = search.current();
    current = current.next();
    if(!current.size())
      current = $('#header .search-form form .results li:first');
    $('#header .search-form form .results li').removeClass('current');
    current.addClass('current');
  }
  search.previous = function() {
    var current = search.current();
    current = current.prev();
    if(!current.size())
      current = $('#header .search-form form .results li:last');
    $('#header .search-form form .results li').removeClass('current');
    current.addClass('current');
  }
  search.init = function(container) {
    var label = container.find('#header .edit-form label span').html();
    container.find('#header .search-form label').remove();
    container.find('#header .search-form form').attr('autocomplete', 'off').prepend(container.find('#header .search-form #actionsView .button').clone().attr('type', 'hidden').attr('class', ''));
    container.find('#header .search-form #actionsView').remove();
    container.find('#header .search-form li input').attr('alt', label).blur(search.blur).focus(search.focus).keyup(search.changed);
    $.proxy(search.blur, container.find('#header .search-form li input'))();
    
    container.find('.search-form .listing').each(function() {
      var form = $(this).parents('.search-form').find('.edit-form').addClass('collapsible');
      form.find('h1').addClass('toggler');
      collapsible.create(form);
    });
  };
  
  initialization.register(search.init);
  
})(jQuery);
