var datetime = {};

(function($) {
  
  datetime.init = function(container) {
    container.find('input.date').attr('autocomplete', 'off').each(function() {
      $(this).datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: $(this).data('format').replace('yy', 'y')
      });
    });
    container.find('input.spinbox.hours:not(.spinbox-active)').attr('autocomplete', 'off').spinbox({
      min: 0,
      max: 23,
      step: 1,
      bigStep: 5,
      mousewheel: false,
      keys: [/[0-9]/,9,13,8,46,33,34,37,38,39,40,96,97,98,99,100,101,102,103,104,105,109,188,190]
    });
    container.find('input.spinbox.minutes:not(.spinbox-active)').attr('autocomplete', 'off').spinbox({
      min: 0,
      max: 59,
      step: 1,
      bigStep: 10,
      mousewheel: false,
      keys: [/[0-9]/,9,13,8,46,33,34,37,38,39,40,96,97,98,99,100,101,102,103,104,105,109,188,190]
    });
  }
  
  $(document).ready(function() {
    datetime.init($(document));
  });
})(jQuery);
