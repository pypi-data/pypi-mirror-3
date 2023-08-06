var notifications = {};
(function($) {

  notifications.lists = false;
  notifications.counts = false;
  notifications.updating = false;
  notifications.read_timer = false;
  notifications.listeners = [];

  notifications.init = function() {
    notifications.lists = $('.notifications');
    notifications.counts = $('.notifications-count');
    if(!notifications.lists.size())
      return;
    $('body').unbind('mousemove', notifications.update).mousemove(notifications.update);
    notifications.lists.find('li.new').hover(notifications.over, notifications.out);
    notifications.lists.find('.new a:not(.delete)').click(notifications.read);
    notifications.lists.find('a.delete').unbind('click').click(notifications.del);
    $('.portletNotification:not(.open) .portletItem').hide();
    $('.portletNotification .portletHeader').css('cursor', 'pointer').unbind('click', notifications.toggle).click(notifications.toggle);
  }

  notifications.toggle = function(e) {
    e.preventDefault();
    var portlet = $(this).closest('.portletNotification');
    var item = portlet.find('.portletItem');
    if(portlet.hasClass('open'))
      item.stop().slideUp('fast');
    else
      item.stop().attr('style', '').hide().slideDown('fast');
    portlet.toggleClass('open');
  }

  notifications.del = function(e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var li = $(this).closest('li');
    $.get($(this).attr('href'), {'ajax_load': 1}, function(data) {
      li.removeClass('loading');
      if(data == '0')
        return
      li.fadeOut('fast', function() {
        li.remove();
        notifications.load();
      });
    });
  }

  notifications.over = function(e) {
    if(notifications.read_timer)
      window.clearTimeout(notifications.read_timer);
    notifications.read_timer = window.setTimeout($.proxy(notifications.read, this), 2000);
  }

  notifications.out = function(e) {
    if(notifications.read_timer)
      window.clearTimeout(notifications.read_timer);
  }

  notifications.read = function() {
    if($(this).is('a'))
      var url = $(this).attr('href');
    else
      var url = $(this).closest('ul').data('url') + '/read?id=' + $(this).data('id');
    var li = $(this).closest('li');
    $.get(url, {'ajax_load': 1, 'c': (new Date()).getTime()}, function(data) {
      if(!data)
        return;
      li.unbind('mouseover', notifications.over);
      li.unbind('mouseout', notifications.out);
      li.find('a:not(.delete)').unbind('click', notifications.read);
      li.removeClass('new');
      notifications.updateCounts();
    });
  }

  notifications.updateCounts = function() {
    if(!notifications.counts.size())
      return;
    $.get(notifications.lists.data('url') + '/unread', {'c': (new Date()).getTime()}, function(data) {
      notifications.counts.html(data);
    });
  }

  notifications.update = function(e) {
    if(notifications.updating)
      return;
    notifications.updating = true;
    notifications.updateCounts();
    $.get(notifications.lists.data('url') + '/news', {'latest': notifications.lists.find('li:first').data('id'), 'c': (new Date()).getTime()}, function(data) {
      if(data != '1') {
        window.setTimeout(function() {
          notifications.updating = false;
        }, 5000);
        return;
      }
      notifications.load();
    });
  }

  notifications.load = function() {
    notifications.updating = true;
    notifications.lists.addClass('loading');
    notifications.lists.find('li').fadeTo('fast', 0.1);
    $.get(notifications.lists.data('url'), {'c': (new Date()).getTime()}, function(data) {
      if(!data) {
        notifications.lists.find('li').fadeTo('fast', 1);
        notifications.lists.removeClass('loading');
        return;
      }
      window.setTimeout(function() {
        notifications.lists.each(function() {
          var list = $(this);
          var new_list = $(data).hide();
          if(list.find('li').size()) {
            list.find('li').fadeOut('fast', function() {
              list.replaceWith(new_list);
              new_list.fadeIn('fast');
            });
          } else {
            list.replaceWith(new_list);
            new_list.fadeIn('fast');
          }
        });
        notifications.init();
        notifications.publish();
        notifications.lists.removeClass('loading');
        window.setTimeout(function() {
          notifications.updating = false;
        }, 5000);
      }, 500);
    });
  }

  notifications.publish = function() {
    for(var i=0; i<notifications.listeners.length; i++)
      notifications.listeners[i]();
  }

  notifications.subscribe = function(listener) {
    notifications.listeners.push(listener);
  }

  $(document).ready(notifications.init);

})(jQuery)