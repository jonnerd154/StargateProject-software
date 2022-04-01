var symbols = [] // This array will be populated by an ajax request

function init_pulldowns(){
  for(i=1;i<=6;i++){
    $('#symbol_' + i).ddslick({
      data:symbols,
      //width:300,
      selectText: "Symbol " + i,
      imagePosition:"right",
      onSelected: function(selectedData){
          //callback function: do something with selectedData;
          // TODO: Disable this symbol in the other menus
      }
    }); // End ddslick init
  } // End for

} // End init_pulldowns

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
  $.get('stargate/get/system_info')
    .done(function(data) {

      // Hide the offline modal
      hideOfflineModal()

      // Update the UI
      if (data.local_stargate_address_string){

        // Display the configured local address
        $('#localStargateAddress').html("<div id='lcl_addr_image_container'></div>")

        // If we don't have a Subspace IP address configured, offer the config button
        if ( data.subspace_ip_address_config == null || data.subspace_ip_address_config == "" ){
          $('#localStargateAddress').html( $('#localStargateAddress').html() + "<button id='config-lcl-sg-addr'>Configure</button>")
        }

        // Load the current address in images
        html = ""
        for (i=0;i<6;i++){
          imageUrl = "/chevrons/" + String(data.local_stargate_address[i]).padStart(3, '0');
          imageHtml = "<img src='" + imageUrl + "' alt='" + data.local_stargate_address[i] + "'>"
          html += imageHtml
        }
        html += "<span style='padding: 10px;'>" + data.local_stargate_address_string + "</span>"
        $('#lcl_addr_image_container').html(html)

      }
      else{
        $('#localStargateAddress').html("<button id='config-lcl-sg-addr'>Configure</button>")
      }

      // Setup the "Configure Local Address" button on-click handler
      $( "#config-lcl-sg-addr" ).button().on( "click", function() {
        $( "#dialog-form" ).dialog( "open" );

          // Load the current address into the form
          for (i=0;i<6;i++){
            pulldown = $('#symbol_' + (i+1).toString())
            value = data.local_stargate_address[i]-1 // Minus 1 because these are indexes, not values we're setting.
            setPulldownValue( pulldown, value )
          }
      });

      $('#gateName').html(data.gate_name)
      $('#galaxy').html(data.galaxy)
      $('#lanIPAddress').html(data.lan_ip_address)
      $('#softwareVersion').html(data.software_version)
      $('#softwareUpdateTime').html(data.software_update_last_check)
      $('#softwareUpdateStatus').html(data.software_update_status)
      $('#pythonVersion').html(data.python_version)
      $('#fanGateLastUpdate').html(data.fan_gate_last_update)
      $('#fanGateCount').html(data.fan_gate_count)
      $('#lanGateCount').html(data.lan_gate_count)
      $('#standardGateCount').html(data.standard_gate_count)
      $('#dialerMode').html(data.dialer_mode)
      $('#hardwareMode').html(data.hardware_mode)
      $('#volumeAsPercent').html(data.audio_volume)

      $('#stats_dialing_failures').html(data.stats_dialing_failures)
      $('#stats_established_fan_count').html(data.stats_established_fan_count)
      $('#stats_established_fan_mins').html("&nbsp;(" + data.stats_established_fan_mins.toFixed(2) + " Minutes)")
      $('#stats_established_standard_count').html(data.stats_established_standard_count)
      $('#stats_established_standard_mins').html("&nbsp;(" + data.stats_established_standard_mins.toFixed(2) + " Minutes)")
      $('#stats_inbound_count').html(data.stats_inbound_count)
      $('#stats_inbound_mins').html("&nbsp;(" + data.stats_inbound_mins.toFixed(2) + " Minutes)")

      if (data.subspace_public_key){
        $('#publicKey').html(data.subspace_public_key)
      }
      else{
        $('#publicKey').html("n/a")
        $('#subspaceStatus').html("Not Configured")
      }

      if (data.internet_available){
        $('#hasInternet').html("Connected")
      }
      else{
        $('#hasInternet').html("Offline")
      }

      if (data.subspace_available){
        $('#subspaceStatus').html("Connected")
      }
      else{
        $('#subspaceStatus').html("Offline")
      }

      // If we don't have a Subspace IP,
      if (!data.subspace_ip_address_config){

        // ...and we DO have a local_address configured, offer a link to email Kristian
        if (data.local_stargate_address_string){
            emailTo = "kristian@thestargateproject.com"
            subject = "New Stargate"
            body = "Hi Kristian,%0d%0a%0d%0aI'd like to get a Subspace IP address for my new Stargate. Can you set that up?%0d%0a%0d%0a" +
                   "Name/planet: %3CThe name you want in the %22address book%22%3E%0d%0a" +
                   "Email address: %3CYour email address%3E%0d%0a%0d%0a" +
                   "Stargate address: " + data.local_stargate_address_string + "%0d%0a" +
                   "Public key: " + data.subspace_public_key + "%0d%0a" +
                   "%0d%0aThanks,"



                   mailLinkContent = "<a href=\"mailto:" + emailTo + "?subject=" + subject + "&body=" + body + "\">Step 1: Request Access to the Subspace Network</a>"
                   ipConfigLink = "Step 2: <button id='config-subspace-ip-addr'>Configure Subspace IP Address</button>"
            $('#subspaceIPAddress').html(mailLinkContent + "<br>" + ipConfigLink)

            // Setup the "Configure Subspace IP Address" button on-click handler
            $( "#config-subspace-ip-addr" ).button().on( "click", function() {
              $( "#dialog-form-subspace-ip" ).dialog( "open" );
                // Load the current address into the form

            });
        }
        else{
           $('#subspaceIPAddress').html("Not Configured!")
        }
      }
      else{
        $('#subspaceIPAddress').html(data.subspace_ip_address_config)
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      // Show the "we're offline modal"
      showOfflineModal()

      setTimeout(function(){updateInfo( false ); }, poll_delay);
    })

    // Get the symbol configs for the dropdowns
    $.get('stargate/get/symbols')
      .done(function(data) {
        symbols = data.symbols
        init_pulldowns()
    })
}

function setPulldownValue( pulldown, value ){
    pulldown.ddslick('select', {index: value });
}
