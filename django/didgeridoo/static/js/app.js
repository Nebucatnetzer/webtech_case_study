  $("#currency_update").change(function () {
    var currency = $(this).val();
    $.ajax({
      url: '/ajax/currency_update/',
      data: {
        'currency': currency
      },
      dataType: 'json',
      success: function (data) {
        if (data.is_taken) {
          alert("es pop auf! --dies kommt von: static/js/app.js--.");
        }
      }
    });
  });
