var ticketing = {
  
  additional: '.attachments, .hourlyexpenses, .onetimeexpenses, .hidden, .dependencies, .tags, .deactivate_workexpenses, .deactivate_hourlyexpenses, .deactivate_onetimeexpenses'
  
};

(function($) {
  
  ticketing.init = function(container) {
    i18n.translate('More', 'horae.layout', function(more) {
      container.find('.ticket-change-form .contents ul').each(function() {
        var fields = $(this).find(ticketing.additional);
        if(!fields.size())
          return;
        if(!$(this).find('> li.ticketing-additional').size())
          $(this).append('<li class="ticketing-additional"><dl class="collapsible"><dt class="toggler">'+more+'</dt><dd class="contents"><ul /></dd></dl></li>');
        var list = $(this).find('> li.ticketing-additional dd.contents > ul');
        list.append(fields);
        collapsible.init($(this));
      });
    });
  },
  
  initialization.register(ticketing.init);
  
})(jQuery);
