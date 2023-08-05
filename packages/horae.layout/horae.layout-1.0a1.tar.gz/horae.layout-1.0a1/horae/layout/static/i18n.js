var i18n = {
  
  cache : new Array(),
  url : false
  
};

(function($) {
  
  i18n.translate = function(msg, domain, callback) {
    if(i18n.url === false)
      i18n.url = $('body').data('base')+'/@@translate';
    if(typeof i18n.cache[domain] == 'undefined')
      i18n.cache[domain] = new Array();
    if(i18n.cache[domain][msg])
      callback(i18n.cache[domain][msg]);
    $.ajax({
      url: i18n.url,
      data: {
        'msgid': msg,
        'domain': domain
      },
      method: 'GET',
      success: function(data) {
        if(!i18n.cache[domain]) 
          i18n.cache[domain] = {};
        i18n.cache[domain][msg] = data;
        callback(data);
      },
      error: function() {
        callback(msg);
      }
    });
    return;
  }
  
})(jQuery);
