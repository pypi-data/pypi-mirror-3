var listing = {};

(function($) {
  
  listing.init = function(container) {
    container.find('.listing').each(function() {
      listing.create($(this));
    });
    $(document).unbind('scroll').scroll(listing.scroll);
  },
  
  listing.create = function(table) {
    if(table.hasClass('active'))
      return;
    table.addClass('active');
    var head = table.find('thead').clone(true);
    head.wrap('<table class="listing fixed-table-head" />');
    var wrapper = head.closest('table').css({
      'position': 'fixed',
      'margin': '0 0 0 '+table.offset().left+'px',
      'z-index': 1,
      'top': $('#top').height(),
      'width': table.width()
    }).hide();
    wrapper.insertBefore(table);
  }
  
  listing.scroll = function(e) {
    var scrolltop = $(document).scrollTop();
    var scrollleft = $(document).scrollLeft();
    var headerheight = $('#top').height();
    $('.listing:not(.fixed-table-head)').each(function() {
      var top = $(this).find('thead').offset().top;
      var bottom = $(this).offset().top + $(this).height();
      var fixed = $(this).prev('.fixed-table-head');
      var table = $(this);
      if(top < scrolltop + headerheight && bottom > scrolltop) {
        fixed.css('left', -scrollleft);
        if(fixed.css('display') == 'none') {
          fixed.css('width', table.width());
          table.find('thead th').each(function() {
            fixed.find('thead th:eq('+table.find('thead th').index(this)+')').css('width', $(this).width());
          });
          fixed.show();
        }
      } else {
        fixed.hide();
      }
    });
  }
  
  initialization.register(listing.init);
  
})(jQuery);
