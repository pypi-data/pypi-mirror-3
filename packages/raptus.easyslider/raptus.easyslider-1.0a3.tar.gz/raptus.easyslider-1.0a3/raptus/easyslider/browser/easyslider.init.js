(function($) {
  $(document).ready(function() {
    var loaded = false;
    $('.easyslider').loaded(function() {
      if(loaded)
        return;
      loaded = true;
      $('.easyslider').each(function() {
        var classes = $(this).attr('class').split(' ');
        var settings;
        for(var i=0; i<classes.length; i++)
          if(classes[i].substr(0, 11) == 'easyslider-') {
            var settings = easyslider.settings[classes[i].substr(11)];
            break;
          }
        if(!settings)
          settings = easyslider.settings['standard'];
        $(this).easySlider(settings);
      });
    });
  });
})(jQuery);
