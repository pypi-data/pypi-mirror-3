var nestedlist = {};
(function($) {
  
  nestedlist.init = function(container) {
    i18n.translate('Information', 'horae.layout', function(msg) {
      container.find('.nestedlist li > .heading > a.detail').each(function() {
        var info = $('<dl class="collapsible"><dt class="toggler" rel="'+$(this).attr('href')+'?plain=1&selector=.contents">'+msg+'</dt><dd class="contents"></dd></dl>');
        info.insertAfter($(this).parent());
        collapsible.create(info);
      });
    });
  }
  
  initialization.register(nestedlist.init);
  
})(jQuery);
