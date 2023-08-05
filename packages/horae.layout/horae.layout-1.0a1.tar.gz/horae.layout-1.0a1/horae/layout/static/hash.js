(function($) {
  
  $(window).load(function() {
    var hash = document.location.hash;
    if(!hash)
      return;
    var elm = $('a[name="'+hash.substr(1)+'"]');
    if(!elm.size())
      return;
    $(document).scrollTop(elm.offset().top - 50);
  });
  
})(jQuery)
