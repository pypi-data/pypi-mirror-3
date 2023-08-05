var dialogs = {
  
  message : false,
  loading : false
  
};

(function($) {
  
  dialogs.init = function(container) {
    container.find('.button.delete, .menu-actions a[href$="/delete"]').unbind('click').click(dialogs.show);
  }
  
  dialogs.show = function(e) {
    e.preventDefault();
    dialogs.show_loading();
    var params = [];
    var url;
    if($(this).is('form')) {
      params = $(this).serializeArray();
      url = $(this).attr('action');
    } else
      url = $(this).attr('href');
    params.push({'name': 'plain', 'value': 1});
    $.get(url, params, function(data) {
      dialogs.hide_loading();
      var content = $(data);
      content.find('.actionButtons input[name$="cancel"]').click(function(e) {
        e.preventDefault();
        $(this).closest('.ui-dialog-content').dialog('close');
      });
      content.dialog({
        modal: true,
        draggable: false,
        resizable: false,
        show: 'fade',
        dialogClass: 'page-dialog',
        width: 500,
        zIndex: 100000
      });
    });
  }
  
  dialogs.show_message = function(msg, domain) {
    if(dialogs.message == false)
      dialogs.message = $('<div class="content" />');
    dialogs.message.html('');
    i18n.translate(msg, domain, function(msg) {
      dialogs.message.html(msg);
      dialogs.message.dialog({
        modal: true,
        draggable: false,
        resizable: false,
        show: 'fade',
        dialogClass: 'message-dialog',
        zIndex: 100000,
        close: function(event, ui) {
          dialogs.message = false;
        }
      });
    });
  }
  
  dialogs.show_loading = function(msg, domain) {
    if(dialogs.loading == false) {
      dialogs.loading = $('<div class="content" />');
      dialogs.loading.html('');
      dialogs.loading.dialog({
        modal: true,
        draggable: false,
        closeOnEscape: false,
        resizable: false,
        show: 'fade',
        minHeight: 0,
        minWidth: 100,
        zIndex: 100000,
        dialogClass: 'loading-dialog'
      });
    }
    if(msg)
      i18n.translate(msg, domain, function(data) {
        if(dialogs.loading !== false)
          dialogs.loading.html(data);
      });
  }
  
  dialogs.hide_loading = function() {
    if(dialogs.loading !== false) {
      dialogs.loading.dialog('destroy');
      dialogs.loading = false;
    }
  }
  
  initialization.register(dialogs.init);
  
})(jQuery);
