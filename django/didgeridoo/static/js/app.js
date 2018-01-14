  $("#currency_update").change(function () {
    var currency_update = $(this).val();
    $.ajax({
      url: '/ajax/currency_update/',
      data: {
        'currency_update': currency_update
      },
      dataType: 'json',
      success: function (data) {
          alert("es pop auf! --dies kommt von: static/js/app.js--.", data);
      }
    });
  });
