function software_restart() {
    confirm_dialog("Are you sure you want to restart the Gate software?", do_software_restart)
}

function do_software_restart(){
    $.post({
        url: 'stargate/do/restart'
    });
}

function host_reboot() {
    confirm_dialog("Are you sure you want to restart the Raspberry Pi?", do_host_reboot)
}

function do_host_reboot() {
    $.post({
        url: 'stargate/do/reboot'
    });
}

function host_shutdown() {
    confirm_dialog("Are you sure you want to shutdown the Raspberry Pi?", do_host_shutdown)
}

function do_host_shutdown() {
    $.post({
        url: 'stargate/do/shutdown'
    });
}

function confirm_dialog(message, yes_callback){
  $('<div></div>').appendTo('body')
    .html('<div><h6>' + message + '</h6></div>')
    .dialog({
      modal: true,
      title: 'Confirm',
      zIndex: 10000,
      autoOpen: true,
      width: 'auto',
      resizable: false,
      buttons: {
        Yes: function() {
          yes_callback()
          $(this).dialog("close");
        },
        No: function() {
          $(this).dialog("close");
        }
      },
      close: function(event, ui) {
        $(this).remove();
      }
    });
}
