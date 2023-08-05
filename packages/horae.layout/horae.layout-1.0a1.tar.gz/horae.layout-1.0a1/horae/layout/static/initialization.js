var initialization = {
  initializers: []
};
(function($) {
  
  initialization.register = function(inistializer) {
    initialization.initializers.push(inistializer);
  }
  
  initialization.init = function(container) {
    if(!container)
      container = $(document);
    for(var i=0; i<initialization.initializers.length; i++)
      initialization.initializers[i](container);
  }
  
  $(document).ready(function() {
    initialization.init();
  });
  
})(jQuery);
