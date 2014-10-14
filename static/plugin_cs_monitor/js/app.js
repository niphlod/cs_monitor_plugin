$.web2py.fixup_strftime_to_moment = function (strftime) {
  var momentFormat = strftime;
  replacements = {
      'a': 'ddd',
      'A': 'dddd',
      'b': 'MMM',
      'B': 'MMMM',
      'd': 'DD',
      'H': 'HH',
      'I': 'hh',
      'j': 'DDDD',
      'm': 'MM',
      'M': 'mm',
      'p': 'A',
      'S': 'ss',
      'Z': 'z',
      'w': 'd',
      'y': 'YY',
      'Y': 'YYYY',
      '%': '%'
    }
    $.each(replacements, function(key, value) {
        momentFormat = momentFormat.replace('%' + key, value)
    });
    return momentFormat
}

$.web2py.manage_errors = function (target) {
      $('.error_wrapper', target).hide().addClass('help-block')
        .find('.error').prepend($('<span class="glyphicon glyphicon-remove"></span>'))
        .closest('.error_wrapper').slideDown().closest('.form-group').addClass('has-error');
}

$.web2py.flash = function (message, status) {
      if (typeof(status) == 'undefined') status = 'info';
      var flash = $('.flashbs3');
      $.web2py.hide_flash();
      flash.removeClass('alert-info').addClass('alert-' + status).find('.flashcont').html(message);
      flash.find('a').addClass('alert-link');
      if(flash.find('.flashcont').html()) flash.slideDown();
}

$.web2py.hide_flash = function () {
      $('.flashbs3').fadeOut(0).find('.flashcont').html('');
}

$.web2py.event_handlers = function () {
  /*
   * This is called once for page
   * Ideally it should bound all the things that are needed
   * and require no dom manipulations
   */
  var doc = $(document);
  doc.on('click', '.flashbs3', function (e) {
        var t = $(this);
        if(t.css('top') == '0px') t.slideUp('slow');
        else t.fadeOut();
      });
  doc.on('keyup', 'input.integer', function () {
    this.value = this.value.reverse().replace(/[^0-9\-]|\-(?=.)/g, '').reverse();
  });
  doc.on('keyup', 'input.double, input.decimal', function () {
    this.value = this.value.reverse().replace(/[^0-9\-\.,]|[\-](?=.)|[\.,](?=[0-9]*[\.,])/g, '').reverse();
  });
  var confirm_message = (typeof w2p_ajax_confirm_message != 'undefined') ? w2p_ajax_confirm_message : "Are you sure you want to delete this object?";
  doc.on('click', "input[type='checkbox'].delete", function () {
    if(this.checked)
      if(!$.web2py.confirm(confirm_message)) this.checked = false;
  });
  var datetime_format = (typeof w2p_ajax_datetime_format != 'undefined') ? w2p_ajax_datetime_format : "%Y-%m-%d %H:%M:%S";
  doc.on('click', "input.datetime", function () {
    var tformat = $(this).data('w2p_datetime_format');
    var active = $(this).data('w2p_datetime');
    var format = (typeof tformat != 'undefined') ? tformat : datetime_format;
    if(active === undefined) {
      $(this).datetimepicker({
          language:'en',                  //sets language locale
          useStrict: false,               //use "strict" when validating dates
          sideBySide: false,              //show the date and time picker side by side
          format : $.web2py.fixup_strftime_to_moment(format)
      });
      $(this).attr('autocomplete', 'off');
      $(this).data('w2p_datetime', 1);
      $(this).trigger('click');
    }
  });
  var date_format = (typeof w2p_ajax_date_format != 'undefined') ? w2p_ajax_date_format : "%Y-%m-%d";
  doc.on('click', "input.date", function () {
    var tformat = $(this).data('w2p_date_format');
    var active = $(this).data('w2p_date');
    var format = (typeof tformat != 'undefined') ? tformat : date_format;
    if(active === undefined) {
      $(this).datetimepicker({
          language:'en',                  //sets language locale
          useStrict: false,               //use "strict" when validating dates
          sideBySide: false,              //show the date and time picker side by side
          pickTime: false,
          format : $.web2py.fixup_strftime_to_moment(format)
      });
      $(this).data('w2p_date', 1);
      $(this).attr('autocomplete', 'off');
      $(this).trigger('click');
    }
  });
  doc.on('focus', "input.time", function () {
    var active = $(this).data('w2p_time');
    if(active === undefined) {
      $(this).datetimepicker({
          language:'en',                  //sets language locale
          useStrict: false,               //use "strict" when validating dates
          sideBySide: false,              //show the date and time picker side by side
          pickDate: false,
          format : 'HH:MM'
      });
      $(this).attr('autocomplete', 'off');
      $(this).data('w2p_time', 1);
    }
  });
  /* help preventing double form submission for normal form (not LOADed) */
  $(doc).on('submit', 'form', function () {
    var submit_button = $(this).find($.web2py.formInputClickSelector);
    $.web2py.disableElement(submit_button);
  });
  doc.ajaxSuccess(function (e, xhr) {
    var redirect = xhr.getResponseHeader('web2py-redirect-location');
    if(redirect !== null) {
      window.location = redirect;
    };
    /* run this here only if this Ajax request is NOT for a web2py component. */
    if(xhr.getResponseHeader('web2py-component-content') == null) {
      $.web2py.after_ajax(xhr);
    };
  });

  doc.ajaxError(function (e, xhr, settings, exception) {
    /*personally I don't like it.
     *if there's an error it it flashed and can be removed
     *as any other message
     *doc.off('click', '.flash')
     */
    switch(xhr.status) {
    case 500:
      $.web2py.flash(ajax_error_500);
    }
  });
}

$.web2py.main_hook = function() {
      var flash = $('.flashbs3');
      flash.hide();
      if(flash.find('.flashcont').html()) $.web2py.flash(flash.find('.flashcont').html());
      $.web2py.ajax_init(document);
      $.web2py.event_handlers();
      $.web2py.a_handlers();
      $.web2py.form_handlers();
    }