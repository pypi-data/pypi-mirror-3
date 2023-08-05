var notification = {
  
  url: false,
  container: false,
  detail: false,
  updated: true,
  hide: false,
  show: false,
  timer: false,
  update_timer: false,
  updating: false
  
};

(function($) {
  
  notification.init = function(container) {
    notification.listinit(container);
    notification.container = container.find('div.notifications');
    if(!notification.container.size())
      return;
    notification.url = notification.container.find('a').attr('href');
    notification.container.find('a').wrap('<div class="wrapped" />');
    notification.container.hover(notification.show, notification.hide);
    $(document).mousemove(notification.moved);
  }
  
  notification.listinit = function(container) {
    container.find('#content ul.notifications li .button').unbind('click').click(notification.mark);
    container.find('#content ul.notifications li .information').unbind('click').click(notification.information);
    container.find('#content a[href*="view-notifications?mark_all_read=1"]').unbind('click').click(notification.mark_all_read);
    container.find('#content a[href*="view-notifications?amount="]').unbind('click').click(notification.show_more);
  }
  
  notification.mark = function(e) {
    e.preventDefault();
    $.getJSON($(this).attr('href'), {'ajax': 1}, $.proxy(function(data) {
      if(!data)
        return;
      if(data.url.indexOf('unread') > -1) {
        $(this).closest('li').removeClass('unread');
        $(this).addClass('button-alternative');
      } else {
        $(this).closest('li').addClass('unread');
        $(this).removeClass('button-alternative');
      }
      $(this).attr('href', data.url);
      $(this).html(data.label);
      notification.update();
    }, this));
  }
  
  notification.information = function(e) {
    e.preventDefault();
    if($(this).hasClass('loading'))
      return;
    var body = $(this).closest('li').find('.body');
    if(body.size()) {
      if($(this).data('shown')) {
        body.stop().slideUp('fast');
        $(this).data('shown', false);
        $(this).html(notification.show);
        return;
      }
      body.stop().hide().css({
        'height': 'auto',
        'padding': '1em',
        'opacity': 1
      }).slideDown('fast');
      $(this).data('shown', true);
      $(this).html(notification.hide);
      return;
    }
    $(this).addClass('loading');
    $.getJSON($(this).attr('href'), {'ajax': 1}, $.proxy(function(data) {
      if(!data)
        return;
      notification.hide = data.label;
      notification.show = $(this).html();
      $(this).removeClass('loading');
      $(this).html(notification.hide);
      $(this).data('shown', true);
      var body = $('<div class="body" />').hide().append(data.body);
      $(this).closest('li').append(body);
      body.slideDown('fast');
    }, this));
  }
  
  notification.mark_all_read = function(e) {
    e.preventDefault();
    $.getJSON($(this).attr('href'), {'ajax': 1}, function(data) {
      if(!data)
        return;
      $('#content ul.notifications li .button[href*="read="]').each(function() {
        $(this).addClass('button-alternative');
        $(this).html(data.label);
        $(this).attr('href', $(this).attr('href').replace('?read=', '?unread='));
        $(this).closest('li').removeClass('unread');
        notification.update();
      });
    });
  }
  
  notification.show_more = function(e) {
    e.preventDefault();
    if($('#content ul.notifications').hasClass('loading'))
      return;
    $('#content ul.notifications').addClass('loading');
    $.getJSON($(this).attr('href').replace(/amount=[0-9]+/, 'amount=25'), {'ajax': 1, 'start': $('#content ul.notifications li:last a.button').attr('href').replace(/^.+read=([0-9]+)$/, '$1')}, $.proxy(function(data) {
      if(!data)
        return;
      if(!data.has_more)
        $(this).remove();
      $('#content ul.notifications').append($(data.entries).find('li'));
      $('#content ul.notifications').removeClass('loading');
      notification.listinit();
    }, this));
    
  }
  
  notification.moved = function(e) {
    if(notification.updating || notification.update_timer)
      return;
    notification.update_timer = window.setTimeout(notification.update, 1000*20);
  }
  
  notification.update = function() {
    if(notification.updating)
      return;
    notification.updating = true;
    $.getJSON(notification.url, {'ajax': 'unread'}, function(data) {
      notification.updating = false;
      if(!data)
        return;
      notification.container.find('.wrapped > a').html(data.unread).attr('title', data.message);
      if(data.unread > 0)
        notification.container.find('.wrapped > a').addClass('unread');
      else
        notification.container.find('.wrapped > a').removeClass('unread');
      notification.updated = true;
    });
  }
  
  notification.show = function(e) {
    if(notification.timer)
      window.clearTimeout(notification.timer);
    if(notification.container.hasClass('shown'))
      return;
    notification.container.addClass('shown');
    if(!notification.detail) {
      notification.detail = $('<div class="detail" />').hide();
      notification.container.append(notification.detail);
    } else if(!notification.updated) {
      notification.detail.show();
      return;
    }
    notification.detail.html('').addClass('loading').show();
    $.get(notification.url, {'ajax': 'simple', 'amount': 20}, function(data) {
      notification.updated = false;
      notification.detail.removeClass('loading').html(data);
      notification.detail.find('li').hover(notification.over, notification.out);
    });
  }
  
  notification.hide = function(e) {
    notification.timer = window.setTimeout(function() {
      notification.container.removeClass('shown');
      notification.detail.hide();
    }, 250);
  }
  
  notification.over = function(e) {
    if(!$(this).hasClass('unread'))
      return;
    notification.timer = window.setTimeout($.proxy(function() {
      $.get(notification.url, {'ajax': 1, 'read': $(this).data('id')}, $.proxy(function(data) {
        if(!data)
          return;
        $(this).removeClass('unread');
        notification.update();
      }, this));
    }, this), 1000*2);
  }
  
  notification.out = function(e) {
    if(notification.timer)
      window.clearTimeout(notification.timer);
  }
  
  initialization.register(notification.init);
  
})(jQuery);
