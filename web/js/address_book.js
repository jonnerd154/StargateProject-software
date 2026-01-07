function update_address_book(){
  $.ajax({
      dataType: "json",
      url: "/stargate/get/address_book",
      data: {
          type: "all"
      },
      success: function( json ) {
          summary = json['summary']
          addresses = json['address_book']
          galaxy_path = json['galaxy_path']
          load_address_book()
      },
      error: function (xhr, textStatus, errorThrown){
          console.log("Failed to load Address Book from Stargate")
          $("<div>Failed to load Address Book from Stargate</div>").dialog();
      }

  });
}
function load_address_book(){
    $("#address_book_summary").html('')
    nameLookup = {
      "fan": "Subspace Gates",
      "lan": "LAN Gates",
      "standard": "Standard Gates",
    }
    $.each(summary, function( name, count) {
        $("#address_book_summary").append("<span class='address-book-row-"+name+"'><span class='gate_count' style='padding:0px;'>" + count + "</span> "+ nameLookup[name] + "</span>")
    });

    $.each(addresses, function( index, value ) {
        address_raw = value.gate_address
        address_string = address_raw.join("-");
        is_gate_online = value.is_gate_online
        if (is_gate_online == 0){
                is_gate_online = ""
        } else {is_gate_online = "Online"}

        $.each(address_raw, function( index, value) {
            value=("000" + value).substr(-3,3);
            address_raw[index] = '<img class="address-book-glyph" src="chevrons/'+galaxy_path+'/'+value+'.svg" />';
        });

        address = address_raw.join("");

        $("#presets").append('<div class="address-book-row address-book-row-'+value.type+' col-sm " onclick="window.location = \'/stargate/dial?address=' +
          address_string + '\';"><div class="address-book-col-planet-names">' + value.name + '</div><div class="address-book-col-glyphs">' + address + '</div><div class="address-book-is-online">' + is_gate_online + '</div></div>' );
    });
}

function poll_success(singleShot, data){
  // If we're coming back from being offline, update the address book

  if (!is_online){
    update_address_book()
  }

  // Hide the offline modal
  hideOfflineModal()

  poll_delay = poll_delay_default
  // Schedule the next polling
  if ( !singleShot ){
      setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}
