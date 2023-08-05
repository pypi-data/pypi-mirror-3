var calendar = {
  entries: false
};

(function($) {
  
  calendar.init = function(container) {
    calendar.entries = container.find('.calendar .week tbody .entry > div');
    calendar.entries.each(function() {
      $(this).hide().addClass('tooltip');
      $(this).parent().hover(calendar.over, calendar.out).css('cursor', 'pointer');
    });
    calendar.entries.each(function() {
      $('<span />').css({
        'display': 'block',
        'height': $(this).parent().height()
      }).appendTo($(this).parent());
    });
  }
  
  calendar.over = function(e) {
    calendar.entries.hide();
    var position = $(this).position();
    $(this).children('div').css({
      'left': position.left-1,
      'top': position.top-1,
      'min-height': $(this).height()+1,
      'min-width': $(this).width()
    }).show();
  }
  
  calendar.out = function(e) {
    $(this).children('div').hide();
  }
  
  initialization.register(calendar.init);
  
})(jQuery);
