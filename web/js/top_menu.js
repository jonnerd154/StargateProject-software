function software_restart() {
    $.post({
        url: 'stargate/do/restart'
    });
}

function host_reboot() {
    $.post({
        url: 'stargate/do/reboot'
    });
}

function host_shutdown() {
    $.post({
        url: 'stargate/do/shutdown'
    });
}
