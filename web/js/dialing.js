
var first_run = true
var hasSymbols = false
var cancel = false

function doSpeedDial(speed_dial_full_address){
  // Check for preset address in $_GET (via javascript instead of server-side)
  // https://stackoverflow.com/questions/1586330/access-get-directly-from-javascript
  var parts = window.location.search.substr(1).split("&");
  var $_GET = {};
  for (var i = 0; i < parts.length; i++) {
      var temp = parts[i].split("=");
      $_GET[decodeURIComponent(temp[0])] = decodeURIComponent(temp[1]);
  }

  if($_GET.address) {
      var chevrons = $_GET.address.split("-");

      // Set this to true to enable complete auto-dialing, with Origin and center button
      if ( speed_dial_full_address ){
        // Add the home symbol
        chevrons.push("1");

        // Add the center button
        chevrons.push("0");
      }

      // Configure some variable delays between presses to make it more realistic
      $.post( "stargate/do/clear_outgoing_buffer", function( data ) {

        var timeouts = [];
        var delay_total = 0;
          for(i=0;i<10;i++){
            if (i==0){

                // Clear the buffer first
                console.log("Scheduling click for Chevron " + i + " after " + delay_total)
                timeouts.push(0);
            }
            else{
                var delay = Math.floor(1000 * ((Math.random() * 2.5) + 0.5));
                delay_total+=delay
                console.log("Scheduling click for Chevron " + i + " after " + delay_total)
                console.log(delay)

                timeouts.push(delay_total);
            }
          }

          // Schedule the clicks
          for (var i = 0; i < chevrons.length; i++) {
              clickChevron(chevrons,i);
          }

          cancel = false
          
          // This will create a new entry in the browser's history, without reloading, so refreshing won't start dialing again.
          window.history.pushState({}, "", '/index.htm');
          function clickChevron(chevrons, i) {
              setTimeout(function() { if (!cancel){ $("#chevron"+chevrons[i]).click() } }, timeouts[i]);
          }
      });
    }
}

function loadDHDSymbols(){
  $.get('stargate/get/dhd_symbols')
      .done(function(data) {

          $('.chevrons').html('')

          // Add the symbols
          for (var i = 0; i < data.length; i++) {
              html = '<div class="chevron" num="' + data[i]['index'] + '" id="chevron' + data[i]['index'] + '"><img class="glyph" src="' + data[i]['imageSrc'] + '" alt="' + data[i]['name'] + '"/></div>'
              $('.chevrons').append(html)
              //Do something
          }

          // Add the Center Button
          html = '<div class="chevron" num="0" id="chevron0"><img id="center_button_image" src="img/center_button.png" alt="Center Button" /></div>'
          $('.chevrons').append(html)

          html = '<div class="chevron" num="-1" id="abort-dialing"><img id="abort_button_image" src="img/stop.png" alt="Abort Dialing" /></div>'
          $('.chevrons').append(html)

          // Attach the on-click handlers
          $('div.chevrons div.chevron').click(function() {
              const symbol_number = $(this).attr('num');

              if (symbol_number == -1){
                cancel = true;
              }
              $.post({
                  url: '/stargate/do/dhd_press',
                  data: JSON.stringify({
                      symbol: symbol_number
                  })
              })
              .fail(function() {
                  console.log("Failed to communicate with Stargate")
                  $("<div>Failed to communicate with Stargate</div>").dialog();
              })
              .done(function() {
                  // Call the doPoll() function with single-shot mode so we can update ASAP
                  doPoll( true )
              });
          });

          hasSymbols = true

          // Run the "recover from offline" process
          returnFromOffline()


      })
      .fail(function(jqXHR, textStatus, errorThrown) {
          // Show the "we're offline modal"
          showOfflineModal()

      }

  );
}

function poll_success(singleShot, data){
  if (first_run){
    first_run = false
    doSpeedDial(data.speed_dial_full_address);
  }

  // Run the "recover from offline" process
  returnFromOffline()

  // Update the Wormhole status
  updateWormholeStatus(data)

  // Update the Address buffer and locked chevrons
  updateAddressBuffer(data)

  // Update the Connected Planet status
  updateConnectedPlanetStatus(data)

  // Schedule the next polling
  if ( !singleShot ){
      setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}

function returnFromOffline(){
  if (!hasSymbols){
    loadDHDSymbols();
  }
  hideOfflineModal()
}

function updateConnectedPlanetStatus(data){
    if (data.wormhole_active && data.connected_planet){

        var content = "<p>Connected to " + data.connected_planet
        // If we're connected to a black hole, make some changes
        if (data.black_hole_connected){
            $('body').css('background-color', '#721121')
        }
        else{
            $('body').css('background-color', '#7F95A3')
        }
        content += "</p>"
        $('#connected-planet').html(content)

    }
}

function updateWormholeStatus(data){
    shutdownString = ""
    if ( data.wormhole_open_time > 0 ){
        if ( data.black_hole_connected ){
            timeString = "UNKNOWN: Time Dilation Detected!"
            shutdownString = "&nbsp;&nbsp;&nbsp;&nbsp;Shutdown in " + timeString;

        }
        else{
            timeString = new Date(data.wormhole_time_till_close * 1000).toISOString().substr(14, 5)
            shutdownString = "&nbsp;&nbsp;&nbsp;&nbsp;Shutdown in " + timeString;
        }

        switch ( data.wormhole_active ){
            case "outgoing":
                $('#wormhole-status').html("<p>Active Wormhole (OUTGOING)" + shutdownString + "</p>")
                break

            case "incoming":
                $('#wormhole-status').html("<p>Active Wormhole (INCOMING)" + shutdownString + "</p>")
                break
        }
    }
    else{
        // No wormhole established, reset the UI, and handle "establishing" state
        if(data.wormhole_active && !data.wormhole_open_time){
            $('#wormhole-status').html("<p>Establishing Wormhole");
        }
        else{
            $('#wormhole-status').html("<p>No Active Wormhole");
        }

        $('#connected-planet').html("&nbsp;")
        $('body').css('background-color', '#7F95A3')
    }
}

function updateAddressBuffer(data){

    // If the address buffer is empty, clean things up
    if ( ( data.address_buffer_outgoing.length == 0 &&
         data.address_buffer_incoming.length == 0 ) || // Empty incoming and outgoing buffers
         data.address_buffer_outgoing.length < $(".dial-sequence div").length || // Not in sync with the Stargate
         $(".dial-sequence div").length > 9 ){ // Too many symbols / not in sync with the Stargate

        // Clear the dial-sequence display
        $('.dial-sequence').empty()

        // Make all symbols available again
        $(".chevrons .chevron").removeClass("unavailable");

        // Slow the polling to default
        poll_delay = poll_delay_default

    }
    else{
        // There are symbols in the buffer, we're either established or dialing

        // Adjust the polling rate
        if ( data.wormhole_active ){
            poll_delay = poll_delay_established
        }
        else{
            poll_delay = poll_delay_dialing
        }
    }
    for (i=0;i<data.address_buffer_outgoing.length;i++){

        // Get the symbol_number
        symbol_number = data.address_buffer_outgoing[i]

        // If this symbol isn't in the display, show it.
        if ( $("#dialed-chevron"+symbol_number).length == 0 ){

            // Copy the div from the control panel, wrap it, modify it, and add it to the dial-sequence display
            const thisChevronDivHtml = $("#chevron"+symbol_number).clone().wrap('<div/>').parent().html();
            const newChevron = $(thisChevronDivHtml);
            newChevron.attr('id', "dialed-chevron"+symbol_number);
            newChevron.css('transform', 'rotate(0)');
            newChevron.removeClass('unavailable');
            newChevron.addClass('filter-yellow')
            $('.dial-sequence').append(newChevron);
            setTimeout(function() { newChevron.addClass('show'); }, 10);

            // Grey out this symbol in the control panel
            $("#chevron"+symbol_number).addClass('unavailable')

        }

        // Is this chevron locked? If so, mark it as such
        chevronLocked = i >= data.locked_chevrons_outgoing ? false : true
        if (chevronLocked){
            $("#dialed-chevron"+symbol_number).removeClass('filter-yellow')
            $("#dialed-chevron"+symbol_number).addClass('filter-green')
        }
    }

    // Resize display as required
    if (data.address_buffer_outgoing.length > 7) {
        $('.dial-sequence .chevron').addClass('smaller');
    }
    else {
        $('.dial-sequence .chevron').addClass('small').removeClass('smaller');
    }
}
