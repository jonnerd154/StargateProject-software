// Configuration
var poll_delay_default = 5000
var poll_delay_dialing = 500
var poll_delay_established = 1000

// State variables
var poll_delay = poll_delay_default
var is_online = false

var offline_modal = $('<div id="offline-modal" title="Stargate is Offline"><span id="dialogMsg">Unable to communicate with the Stargate. <br><br>Ensure that the Stargate software is running.</span></div>');
offline_modal.dialog({
    autoOpen: false,
    modal: true,
    dialogClass: "no-close",
});

function showOfflineModal(){
    offline_modal.dialog("open");
}

function hideOfflineModal(){
    offline_modal.dialog("close");
}

function offline_handler(singleShot, jqXHR, textStatus, errorThrown){
  // Show the "we're offline modal"
  showOfflineModal()

  // Slow the polling rate to default
  poll_delay = poll_delay_default

  // Schedule the next polling
  if ( !singleShot ){
      setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}

function doPoll( singleShot = false ){
    $.get('stargate/get/dialing_status')
        .done(function(data) {
            poll_success(singleShot, data) // Defined in specific pages, behavior varies
            is_online = true

        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            is_online = false
            offline_handler(singleShot, jqXHR, textStatus, errorThrown) // Defined in specific pages, behavior varies
        }
    );
}
