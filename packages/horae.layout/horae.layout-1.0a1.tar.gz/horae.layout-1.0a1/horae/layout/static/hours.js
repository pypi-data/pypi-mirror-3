var hours = {};
(function($) {
  
  hours.init = function(container) {
    container.find('input[name$="_hours"], input[name$="minimum_entry_length"]').addClass('spinbox').spinbox({
      min: 0,
      step: 0.25,
      bigStep: 1,
      mousewheel: false,
      keys: [/[0-9]/,9,13,8,46,33,34,37,38,39,40,96,97,98,99,100,101,102,103,104,105,109,188,190]
    });
    container.find('input[name$="_expense"]').addClass('spinbox').spinbox({
      min: 0,
      step: 100,
      bigStep: 500,
      mousewheel: false,
      keys: [/[0-9]/,9,13,8,46,33,34,37,38,39,40,96,97,98,99,100,101,102,103,104,105,109,188,190]
    });
    
    // Ticket change
    container.find('input[name$="_hours"]').each(function() {
      var name = $(this).attr('name').replace('_hours', '');
      var form = $(this).parents('form');
      if(!form.find('input[name="'+name+'_start.date:record"]').size() ||
         !form.find('input[name="'+name+'_start.hours:record"]').size() ||
         !form.find('input[name="'+name+'_start.minutes:record"]').size() ||
         !form.find('input[name="'+name+'_end.date:record"]').size() ||
         !form.find('input[name="'+name+'_end.hours:record"]').size() ||
         !form.find('input[name="'+name+'_end.minutes:record"]').size())
        return;
      container.find('input[name="'+name+'_hours"]').addClass('hourInput');
      var range = {
        start : {
          date: form.find('input[name="'+name+'_start.date:record"]'),
          hours: form.find('input[name="'+name+'_start.hours:record"]'),
          minutes: form.find('input[name="'+name+'_start.minutes:record"]')
        },
        end : {
          date: form.find('input[name="'+name+'_end.date:record"]'),
          hours: form.find('input[name="'+name+'_end.hours:record"]'),
          minutes: form.find('input[name="'+name+'_end.minutes:record"]')
        },
        hours : $(this)
      }
      function hours2datetime(e) {
        var range = parseFloat(this.hours.val())*60*60*1000;
        var date = new Date();
        var end = this.end.date.datepicker('getDate');
        if(end == null) {
          end = new Date();
          this.end.date.datepicker('setDate', end);
        }
        if(this.end.hours.val())
          end.setHours(parseInt(this.end.hours.val()));
        else
          this.end.hours.val(end.getHours());
        if(this.end.minutes.val())
          end.setMinutes(parseInt(this.end.minutes.val()));
        else
          this.end.minutes.val(end.getMinutes());
        date.setTime(end.getTime() - range);
        this.start.date.datepicker('setDate', date);
        this.start.hours.val(date.getHours());
        this.start.minutes.val(date.getMinutes());
      }
      range.hours.blur($.proxy(hours2datetime, range));
      function datetime2hours(e) {
        var hours = (this.end.date.datepicker('getDate').getTime() - this.start.date.datepicker('getDate').getTime())/1000/60/60 +
                    (parseInt(this.end.hours.val()) - parseInt(this.start.hours.val())) + 
                    (parseInt(this.end.minutes.val()) - parseInt(this.start.minutes.val()))/60;
        this.hours.val(hours);
      }
      range.start.date.blur($.proxy(datetime2hours, range));
      range.start.hours.blur($.proxy(datetime2hours, range));
      range.start.minutes.blur($.proxy(datetime2hours, range));
      range.end.date.blur($.proxy(datetime2hours, range));
      range.end.hours.blur($.proxy(datetime2hours, range));
      range.end.minutes.blur($.proxy(datetime2hours, range));
      range.hours.focus($.proxy(datetime2hours, range));
    });
    
    // Planned resources
    container.find('input[name="percentage_max"]').each(function() {
      var form = $(this).parents('form');
      var hours = {
        hours: form.find('input[name="form.hours"]'),
        percentage: form.find('input[name="form.percentage"]'),
        estimated: parseFloat(form.find('input[name="estimated"]').val())
      }
      if(!hours.hours.size() || !hours.percentage.size())
        return;
      hours.percentage.addClass('spinbox').spinbox({
        min: 0,
        max: parseFloat($(this).val()),
        step: Math.ceil(parseFloat($(this).val())/5)/10,
        bigStep: Math.ceil(parseFloat($(this).val()))/10,
        mousewheel: false,
        keys: [/[0-9]/,9,13,8,46,33,34,37,38,39,40,96,97,98,99,100,101,102,103,104,105,109,188,190]
      });
      hours.hours.addClass('spinbox').spinbox({
        min: 0,
        max: parseFloat(form.find('input[name="hours_max"]').val()),
        step: Math.ceil(parseFloat(form.find('input[name="hours_max"]').val())/5)/10,
        bigStep: Math.ceil(parseFloat(form.find('input[name="hours_max"]').val()))/10,
        mousewheel: false,
        keys: [/[0-9]/,9,13,8,46,33,34,37,38,39,40,96,97,98,99,100,101,102,103,104,105,109,188,190]
      });
      function hours2percentage(e) {
        if(!this.hours.val())
          this.hours.val('0');
        this.percentage.val(parseFloat(this.hours.val())/this.estimated*100);
      }
      function percentage2hours(e) {
        if(!this.percentage.val())
          this.percentage.val('0');
        this.hours.val(parseFloat(this.percentage.val())/100*this.estimated);
      }
      hours.hours.blur($.proxy(hours2percentage, hours));
      hours.percentage.blur($.proxy(percentage2hours, hours));
      $.proxy(percentage2hours, hours)();
    });
  }
  
  initialization.register(hours.init);
  
})(jQuery);
