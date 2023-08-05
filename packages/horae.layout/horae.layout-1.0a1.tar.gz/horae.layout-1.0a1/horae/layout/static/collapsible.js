var collapsible = {};

(function($) {
  
  collapsible.init = function(container) {
    container.find('.collapsible').each(function() {
      collapsible.create($(this));
    });
  },
  
  collapsible.create = function(item) {
    if(item.hasClass('active'))
      return;
    item.addClass('active').find('.contents').hide().wrapInner('<div />');
    item.find('.toggler').click(function() {
      if($(this).attr('rel')) {
        $(this).addClass('loading');
        $.ajax({
          url: $(this).attr('rel'),
          success: $.proxy(function(data) {
            $(this).attr('rel', '');
            $(this).parents('.collapsible').find('.contents > div').html(data);
            collapsible.toggle($(this));
            $(this).removeClass('loading');
          }, this),
          error: $.proxy(function() {
            $(this).removeClass('loading');
          }, this)});
      } else
        collapsible.toggle($(this));
    });
  }
  
  collapsible.toggle = function(toggler) {
    if($(toggler).closest('.listing').size() && !$(toggler).hasClass('open')) {
      $(toggler).closest('.listing').find('.collapsible .toggler.open').each(function() {
        collapsible.toggle(this);
      });
    }
    $(toggler).closest('.collapsible').find('.contents').stop().slideToggle('fast');
    $(toggler).toggleClass('open');
  }
  
  initialization.register(collapsible.init);
  
})(jQuery);
