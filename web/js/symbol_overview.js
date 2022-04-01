function updateInfo(){

  $.ajax({
      url: '/stargate/get/symbols_all',
      success: function (response) {
        var trHTML = '';
        $.each(response, function (paramName, item) {
            trHTML += getHTMLTableRow(paramName, item)
        });
        $('#symbol_overview_table').html("\
            <tr>\
                <th>Symbol</th>\
                <th>Index</th>\
                <th>Name</th>\
                <th>Keyboard Mapping</th>\
            </tr>");

        $('#symbol_overview_table').append(trHTML);

      }
  });
}

function getHTMLTableRow(paramName, data){
  return '<tr><td><img src="' + data.imageSrc + '" height="50"/></td><td>' + data.index + '</td><td>' +
    '<a target="_blank" href="https://en.wikipedia.org/wiki/'+ data.name + '">'+ data.name + '</a></td><td>' + data.keyboard_mapping + '</td></tr>';
}
