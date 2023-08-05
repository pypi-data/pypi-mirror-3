(function($) {
  
  dashboard.ticketing = {
    subscribed: false
  }
  
  dashboard.ticketing.init = function(container) {
    var widgets = container.find('.dashboard-widget.timetracking-widget');
    if(container.parents('.dashboard-widget.timetracking-widget').size())
      widgets = container.parents('.dashboard-widget.timetracking-widget');
    widgets.each(function() {
      if(!$(this).find('li.workexpense').size())
        return;
      var selected = $(this).find('li.ticket .value input.radioType:checked').closest('label');
      if(selected.size())
        dashboard.ticketing.changed(selected);
      $(this).find('li.ticket .value label').each(function() {
        $(this).unbind('click').click(dashboard.ticketing.click);
        $(this).find('input:radio').unbind('focus').focus(dashboard.ticketing.focus);
      });
      if(dashboard.ticketing.subscribed)
        return;
      autocomplete.subscribe(dashboard.ticketing.changed);
      dashboard.ticketing.subscribed = true;
    });
  }
  
  dashboard.ticketing.changed = function(item) {
    var id = item.find('input:radio').val();
    if(item.closest('form').data('current') == id)
      return;
    item.closest('form').data('current', id);
    $.getJSON(item.closest('form').data('actual').replace(/index$/, 'available-resources'), {id: id}, $.proxy(function(data) {
      if(this.data('current') != data.id)
        return;
      this.find('li.workexpense select option').attr('disabled', 'disabled');
      var selected = false;
      for(var i=0; i<data.resources.length; i++) {
        this.find('li.workexpense select option[value="'+data.resources[i]+'"]').removeAttr('disabled');
        if(this.find('li.workexpense select option[value="'+data.resources[i]+'"]:selected').size())
          selected = true;
      }
      if(!selected)
        this.find('li.workexpense select option').removeAttr('selected');
    }, item.closest('form')));
    item.unbind('click').click(dashboard.ticketing.click);
    item.find('input:radio').unbind('focus').focus(dashboard.ticketing.focus);
  }
  
  dashboard.ticketing.click = function(e) {
    dashboard.ticketing.changed($(this));
  }
  
  dashboard.ticketing.focus = function(e) {
    dashboard.ticketing.changed($(this).closest('label'));
  }
  
  dashboard.register(dashboard.ticketing.init);
  dashboard.register(datetime.init);
  dashboard.register(autocomplete.init);
  
})(jQuery);
