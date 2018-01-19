  $("#id_currency_update").change(function () {
    var currency_update = $(this).val();
    $("#id_currency_update").val(currency_update);
    $.ajax({
      url: '/ajax/currency_update/',
      data: {
        'currency_update': currency_update
      },
      dataType: 'json',
      success: function (data) {
        var foo = jQuery.parseJSON(data);
        alert("es pop auf! --dies kommt von: static/js/app.js--." + foo.currency_update);

      }
    });
  });

  //document.getElementById('id_currency_update').getElementsByTagName('currency_update')
  //$("#id_currency_update").val('USD').selected = 'selected';

  //https://stackoverflow.com/a/30489067/4061870
  // var obj = document.getElementById("id_currency_update");
  // for(i=0; i<obj.options.length; i++){
  //   if(obj.options[i].value == "USD"){
  //     obj.selectedIndex = i;
  //   }
  // }

  // var e document.getElementById("id_currency_update");
  //e.value = currency_update;
