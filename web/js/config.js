function poll_success(singleShot, data){
  // Hide the offline modal
  hideOfflineModal()

  // If we're recovering from being offline, refresh
  if (!is_online){
    updateInfo()
  }
  is_online = true

  poll_delay = poll_delay_default

  // Schedule the next polling
  if ( !singleShot ){
    setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}

function updateInfo(){
  $.ajax({
      url: '/stargate/get/config',
      success: function (response) {
        var trHTML = '';
        var lastGroup = false

        $('#records_table').html("");

        $.each(response, function (paramName, item) {

            paramPrettyName = toProperCase(paramName)
            group = getParamGroupByPrettyName(paramPrettyName)

            if (lastGroup == false || lastGroup != group){
              trHTML += "<br><h3>" + group + " Configurations" +"</h3>"
            }
            lastGroup = group

            trHTML += getHTMLTableRow(paramName, paramPrettyName, item, group)
        });

        trHTML +='<br><button type="submit" class="btn btn-primary">Submit</button><br><br>'

        $('#records_table').append(trHTML);

        initFormSubmitHandler()

      }
  });
}

function getParamGroupByPrettyName(paramPrettyName){

  // Hacky, but gets the job done
  groups = {
      "Audio": "Audio",
      "Chevron": "Chevron Motor",
      "Control": "Stargate Control API",
      "DHD": "Dial Home Device (DHD)",
      "Dialing": "Dialing",
      "Fan": "Fan Gate Update",
      "Software": "Software Update",
      "Stepper": "Stepper",
      "Subspace": "Subspace Network",
      "Wormhole": "Wormhole Max Time"
  }

  compound_groups = {
    "Chevron Config": "Chevron GPIO",
  }
  group_basic = paramPrettyName.split(' ')[0]
  group_basic_2 = paramPrettyName.split(' ')[1]
  group_compound = group_basic + " " + group_basic_2

  // No group match, misc.
  if ( !groups[group_basic] && !compound_groups[group_compound]){
    return "Miscellaneous"
  }
  else if ( compound_groups[group_compound] ){
    return compound_groups[group_compound]
  }
  return groups[group_basic]

}
function getHTMLTableRow(paramName, paramPrettyName, data, group){
  inputField = getHTMLField( paramName, data )
  if (!data.units){
    data.units = ""
  }
  else{
    data.units = "("+ data.units +") "
  }
  return '<div class="form-group-'+group+'">\
    <label for="'+paramName+'">' + paramPrettyName + '</label>\
    <span style="float: right;">' + inputField + '</span><br><br>\
    <small class="form-text">' + data.units + data.desc + '</small>\
  </div>'
}

function getHTMLField( paramName, data ){
  switch( data.type ){
    case "bool":
      return getHTMLBool( paramName, data )
    case "int":
      return getHTMLInt( paramName, data )
    case "float":
      return getHTMLFloat( paramName, data )
    case "str":
      return getHTMLString( paramName, data )
    case "str-datetime":
        return getHTMLDateTime( paramName, data )
    case "str-enum":
        return getHTMLStringEnum( paramName, data )
    case "str-ip":
        return getHTMLStringIPAddress( paramName, data )
    default:
      // If a type isn't specified, just print the raw value without a field
      return data.value
  }
}

function getHTMLBool( paramName, data ){
  if ( data.protected ) return data.value

  if ( data.value ){
    valueTrue = " SELECTED"
    valueFalse = ""
  }
  else{
    valueTrue = ""
    valueFalse = " SELECTED"
  }
  return "\
      <select name='" + paramName + "'>\
        <option value='true' " + valueTrue + ">True</option>\
        <option value='false' " + valueFalse + ">False</option>\
      </select>"

}

function getHTMLInt( paramName, data ){
  if ( data.protected ) return data.value
  return "<input type='number' name='" + paramName + "' value='" + data.value + "' step='1' min='" + data.min_value + "' max='" + data.max_value + "'>"
}

function getHTMLFloat( paramName, data ){
  if ( data.protected ) return data.value
  return "<input type='number' name='" + paramName + "' value='" + data.value + "' step='0.001' min='" + data.min_value + "' max='" + data.max_value + "'>"
}

function getHTMLString( paramName, data ){
  if ( data.protected ) return data.value
  return "<input type='text' name='" + paramName + "' value='" + data.value + "'>"
}

function getHTMLStringIPAddress( paramName, data ){
  if ( data.protected ) return data.value
  return "<input type='text' name='" + paramName + "' value='" + data.value + "'>"
}

function getHTMLStringEnum( paramName, data ){
  if ( data.protected ) return data.value
  html = "<select name='" + paramName + "'>"
  $.each(data.enum_values, function (index, value) {
    selected = ""
    if( value == data.value ) selected = " SELECTED"
    html += "<option value='" + value + "'" + selected + ">" + toProperCase(value) + "</option>"
  })
  html += "</select>"
  return html
}

function getHTMLDateTime( paramName, data ){
  now = moment()
  then = moment(data.value)
  return then.from(now);
}

function toProperCase(str){
  str = str.replace(/_/g, " "); // Replace underscores with spaces

  const abbrv = [ "DHD", "HTTP", "API", "IP", "URL", "LED" ]
  // Capitalize first letter of each word
  const words = str.split(" ");
  for (let i = 0; i < words.length; i++) {
      // If this is a common abbreviation, Capitalize the whole thing
      if ( abbrv.includes(words[i].toUpperCase()) ){
          words[i] = words[i].toUpperCase()
      }
      else{
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
      }
  }
  return words.join(" ");
}

var form_is_init = false
function initFormSubmitHandler(){
  if( !form_is_init ){
    form_is_init = true
    $("#config").submit(function(e) {

        // Execution of the normal/non-jquery form submission.
        e.preventDefault();
        e.stopPropagation();

        var form = $(this);

        // TODO: We need to re-pack the dict-type values
        data = getFormDataJson(form)

        $.ajax({
            type: "POST",
            url: 'stargate/update/config',
            dataType : 'json',
            data: data, // serializes and JSON encodes the form's elements.
            success: function(data)
            {
              dialogConfig = {
                modal: true,
                title: "",
                buttons: [
                  {
                    text: "Ok",
                    click: function() {
                      $( this ).dialog( "close" );
                    }
                  }
                ],
                position: {
                  my: "center",
                  at: "center",
                  of: window,
                  collision: "none"
                }
              }
              if( !data.success ){
                dialogConfig['title'] = "Failed to Save Changes"
                $("<div>" + data.message + "</div>").dialog(dialogConfig);
              }
              else{
                dialogConfig['title'] = "Comtrya!"

                if ( Object.entries(data.results).length > 0){
                  listHTML = data.message + "<br>"
                  listHTML += "<ul>"
                  console.log( )
                  for (const [key, value] of Object.entries(data.results)) {
                    console.log(value)
                    listHTML += "<li>" + toProperCase(key) + ": " + value + "</li>"
                  }

                  listHTML += "</ul>"
                }
                else{
                  listHTML = "No changes to be saved"
                }

                $("<div>" + listHTML + "</div>").dialog(dialogConfig);
              }
            },
            error: function(data)
            {
              $("<div>An unknown error occurred</div>").dialog({
                    modal: true,
                    title: "ERROR",
                    buttons: [
                      {
                        text: "Ok",
                        click: function() {
                          $( this ).dialog( "close" );
                        }
                      }
                    ],
                    position: {
                      my: "center",
                      at: "center",
                      of: window,
                      collision: "none"
                    }
                  });
            },
        });
    });
  }
}

function getFormDataJson(form){
  form = form.serializeArray();
  var data = {};
  $(form).each(function(index, obj){
    data[obj.name] = obj.value;
  });
  return JSON.stringify(data);
}
