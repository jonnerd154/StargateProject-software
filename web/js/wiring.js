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
