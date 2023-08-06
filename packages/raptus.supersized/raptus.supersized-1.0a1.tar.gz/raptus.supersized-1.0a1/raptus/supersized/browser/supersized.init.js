(function($) {
  $(document).ready(function() {
    var loaded = false;
    $('.supersized').loaded(function() {
      if(loaded)
        return;
      loaded = true;
      $('.supersized').each(function() {
        var classes = $(this).attr('class').split(' ');
        var settings;
        for(var i=0; i<classes.length; i++)
          if(classes[i].substr(0, 11) == 'supersized-') {
            var settings = supersized.settings[classes[i].substr(11)];
            break;
          }
        if(!settings)
          settings = supersized.settings['standard'];
        $(this).supersized(settings);
      });
    });
  });
})(jQuery);
