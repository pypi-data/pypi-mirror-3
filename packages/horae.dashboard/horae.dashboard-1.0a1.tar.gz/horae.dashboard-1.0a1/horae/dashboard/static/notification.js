(function($) {
  
  dashboard.notification = {}
  
  dashboard.notification.init = function(container) {
    container.find('.dashboard-widget.notifications-widget .notifications li.unread').hover(notification.over, notification.out);
  }
  
  dashboard.register(dashboard.notification.init);
  
})(jQuery);
