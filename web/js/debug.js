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
  $('.debug_button_container .cycleChevronButton').click(function() {
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

  $('.debug_button_container .controlButton').click(function() {
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
