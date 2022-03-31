function poll_success(singleShot, data){
  // Hide the offline modal
  hideOfflineModal()

  poll_delay = poll_delay_default

  // Schedule the next polling
  if ( !singleShot ){
    setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}

function initialize_button_handlers(){
  $('div.button_container div.cycleChevronButton').click(function() {
      const chevron_number = $(this).attr('chevron_number');

      $.post({
          url: 'stargate/do/chevron_cycle',
          data: JSON.stringify({
              chevron_number: chevron_number
          })
      })
      .fail(function() {
          console.log("Failed to communicate with Stargate")
          $("<div>Failed to communicate with Stargate</div>").dialog();
      });
  });

  $('div.button_container div.button').click(function() {
      const action = $(this).attr('action');

      $.post({
          url: 'stargate/do/' + action,
      })
      .fail(function() {
          console.log("Failed to communicate with Stargate")
          $("<div>Failed to communicate with Stargate</div>").dialog();
      });
  });
}
