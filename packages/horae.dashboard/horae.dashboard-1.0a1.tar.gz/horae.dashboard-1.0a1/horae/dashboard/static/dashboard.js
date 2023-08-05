var dashboard = {
  modules: []
};
(function($) {
  
  dashboard.init = function(container) {
    container.find('.dashboard, .dashboard-sidebar').each(function() {
      var width = $(this).width();
      var widgets = $(this).find('.dashboard-widget').each(function() {
        dashboard.init_widget($(this));
      });
      if(widgets.size() > 1) {
        $(this).find('> .row').sortable({
          items: '> .dashboard-widget',
          connectWith: '.row',
          change: dashboard.sort_change,
          update: dashboard.sort_update,
          handle: '.header',
          cursor: 'move',
          tolerance: 'pointer',
          helper: 'clone',
          appendTo: 'body'
        });
      }
      $(this).find('.dashboard-widget.resizable').resizable({
        minWidth: width*4.16667/100+width*6.25/100,
        maxWidth: width,
        minHeight: 100,
        grid: [width*6.25/100, 20],
        resize: dashboard.resize,
        stop: dashboard.resize_stop
      });
      var form = $(this).find('.add-object-form');
      if(!form.size())
        return;
      form.submit(dialogs.show);
    });
    dashboard.init_modules(container);
  }
  
  dashboard.init_widget = function(widget) {
    widget.find('.header .button').unbind('click').click(function(e) {
      e.preventDefault();
      var widget = $(this).closest('.dashboard-widget');
      if(!widget.hasClass('resizable'))
        widget.css('height', widget.height());
      widget.addClass('loading');
      $.get($(this).attr('href'), {'plain': 1}, $.proxy(function(data) {
        var content = $(data);
        content.find('.actionButtons input[name$="cancel"]').click(function(e) {
          e.preventDefault();
          dashboard.reload_widget($(this).closest('.dashboard-widget'));
        });
        content.find('form.delete-form').submit(function(e) {
          e.preventDefault();
          params = $(this).serializeArray();
          $(this).find('.actionButtons input:not(input[name$="cancel"])').each(function() {
            params.push({'name': $(this).attr('name'), 'value': $(this).val()});
          });
          params.push({'name': 'plain', 'value': 1});
          $(this).closest('.dashboard-widget').addClass('loading');
          $.post($(this).attr('action'), params, $.proxy(function(data) {
            var container = $(this).closest('.dashboard');
            $(this).closest('.dashboard-widget').remove();
            dashboard.update_rows(container);
          }, this));
        });
        content.find('form.edit-form').submit(function(e) {
          e.preventDefault();
          params = $(this).serializeArray();
          $(this).find('.actionButtons input:not(input[name$="cancel"])').each(function() {
            params.push({'name': $(this).attr('name'), 'value': $(this).val()});
          });
          params.push({'name': 'plain', 'value': 1});
          $(this).closest('.dashboard-widget').addClass('loading');
          $.post($(this).attr('action'), params, $.proxy(function(data) {
            dashboard.reload_widget($(this).closest('.dashboard-widget'));
          }, this));
        });
        var widget = $(this).closest('.dashboard-widget');
        widget.removeClass('loading').find('.body .wrapper').html('').append(content);
        initialization.init(widget.find('.body .wrapper'));
      }, this));
    });
    var form = widget.find('.body form');
    if(form.size())
      dashboard.init_form(form);
  }
  
  dashboard.init_form = function(form) {
    if(!form.data('actual'))
      return;
    form.submit(function(e) {
      e.preventDefault();
      $(this).closest('.dashboard-widget').addClass('loading');
      params = $(this).serializeArray();
      $(this).find('.actionButtons input:not(input[name$="cancel"])').each(function() {
        params.push({'name': $(this).attr('name'), 'value': $(this).val()});
      });
      params.push({'name': 'plain', 'value': 1});
      $.post($(this).data('actual'), params, $.proxy(function(data) {
        this.find('.body .wrapper').html(data);
        this.removeClass('loading');
        dashboard.init_form(this.find('.body .wrapper form'));
        initialization.init(this.find('.body .wrapper'));
      }, $(this).closest('.dashboard-widget')));
    });
  }
  
  dashboard.init_modules = function(container) {
    for(var i=0; i<dashboard.modules.length; i++)
      dashboard.modules[i](container);
  }
  
  dashboard.reload_widget = function(widget) {
    widget.addClass('loading');
    $.get(widget.data('url'), {'plain': 1}, $.proxy(function(data) {
      var content = $(data);
      this.removeClass('loading').find('.body .wrapper').html('').append(content);
      if(!this.hasClass('resizable'))
        this.css('height', 'auto');
      initialization.init(this.find('.body .wrapper'));
      dashboard.init_widget(this);
    }, widget));
  }
  
  dashboard.register = function(module) {
    dashboard.modules.push(module);
  }
  
  dashboard.update_rows = function(container) {
    var rows = container.find('> .row');
    var widgets = container.find('> .row > .dashboard-widget:not(.ui-sortable-placeholder)');
    var width = 0;
    var row = 0;
    widgets.each(function() {
      var cwidth = dashboard.width($(this));
      var crow = rows.index($(this).closest('.row'));
      if(crow == row) {
        if(width + cwidth > 16) {
          row += 1;
          width = 0;
          if(row >= rows.size()) {
            container.append('<div class="row" />');
            rows = container.find('> .row');
          }
          $(rows.get(row)).prepend($(this));
        }
      } else {
        if(width + cwidth <= 16)
          $(rows.get(row)).append($(this));
        else {
          row = crow;
          width = 0;
        }
      }
      width += cwidth;
    });
  }
  
  dashboard.sort_change = function(event, ui) {
    dashboard.update_rows($(this).closest('.dashboard'));
  }
  
  dashboard.sort_update = function(event, ui) {
    var container = $(this).closest('.dashboard');
    dashboard.update_rows(container);
    container.find('> .row').sortable('destroy').sortable({
      items: '> .dashboard-widget',
      connectWith: '.row',
      change: dashboard.sort_change,
      update: dashboard.sort_update,
      handle: '.header',
      cursor: 'move',
      tolerance: 'pointer',
      helper: 'clone',
      appendTo: 'body'
    });
    var order = [];
    container.find('> .row > .dashboard-widget:not(.ui-sortable-helper)').each(function() {
      order.push($(this).data('id'));
    });
    $.get(container.data('url'), {'order': order.join(',')});
  }
  
  dashboard.width = function(item) {
    return parseInt(item.attr('class').match(/width-(\d+)/)[1]);
  }
  
  dashboard.get_width = function(item) {
    var width = item.closest('.dashboard').width();
    return Math.round((item.width()-width*4.16667/100)/(width*6.25/100)+1);
  }
  
  dashboard.resize = function(event, ui) {
    var width = dashboard.get_width($(this));
    $(this).removeClass('width-'+dashboard.width($(this))).addClass('width-'+width);
    $(this).css('width', (4.16667+(width-1)*6.25)+'%');
    dashboard.update_rows($(this).closest('.dashboard'));
  }
  
  dashboard.resize_stop = function(event, ui) {
    var container = $(this).closest('.dashboard');
    $.get(container.data('url'), {'size': $(this).data('id'), 'width': dashboard.width($(this)), 'height': parseInt($(this).height())});
  }
  
  initialization.register(dashboard.init);
  
})(jQuery);
