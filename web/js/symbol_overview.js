function updateInfo(){

  $.ajax({
      url: '/stargate/get/symbols_all',
      success: function (response) {
        var trHTML = '';
        $.each(response, function (paramName, item) {
            trHTML += getHTMLTableRow(paramName, item)
        });
        $('#records_table').html("\
            <tr>\
                <th>Symbol Number</th>\
                <th>Index</th>\
                <th>Name</th>\
                <th>Keyboard Mapping</th>\
            </tr>");

        $('#records_table').append(trHTML);

      }
  });
}

function getHTMLTableRow(paramName, data){
  return '<tr><td><img src="' + data.imageSrc + '" height="50"/></td><td>' + data.index + '</td><td>' + data.name + '</td><td>' + data.keyboard_mapping + '</td></tr>';
}
