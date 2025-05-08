/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function openDropdown(elementId) {
  document.getElementById(elementId).classList.toggle('show');
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function (event) {
  if (!event.target.matches('.dropbtn')) {
    const dropdowns = document.getElementsByClassName('dropdown-content');
    for (let i = 0; i < dropdowns.length; i++) {
      const openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
};

async function restart() {
  const response = confirm(
    'Are you sure you want to restart the Gate software?',
  );
  if (response) {
    await fetch('/stargate/do/restart', {
      method: 'POST',
      mode: 'no-cors',
    });
  }
}

async function reboot() {
  const response = confirm(
    'Are you sure you want to restart the Raspberry Pi?',
  );
  if (response) {
    await fetch('/stargate/do/reboot', {
      method: 'POST',
      mode: 'no-cors',
    });
  }
}

async function shutdown() {
  const response = confirm(
    'Are you sure you want to shutdown the Raspberry Pi?',
  );
  if (response) {
    await fetch('/stargate/do/shutdown', {
      method: 'POST',
      mode: 'no-cors',
    });
  }
}

function isActive(href) {
  console.log(window.location.href);
  return `href="${href}"` + (window.location.href.includes(href) ? 'class="active-link"' : '');
}

function initializeNavBar() {
  const div = document.createElement('div');
  div.innerHTML = `
  <div class="navigation-menu-wrapper">
      <div class="navigation-menu">
        <a ${isActive('/stargate/dial')}>Home</a>
        <a ${isActive('/stargate/address_book')}>Address Book</a>
        <a ${isActive('/symbol_overview.htm')}>Symbols</a>
        <div class="dropdown">
          <a onclick="openDropdown('menu-dropdown')" class="dropbtn"> Admin </a>
          <div id="menu-dropdown" class="dropdown-content">
            <a ${isActive('/debug.htm')}>Testing / Debug</a>
            <a ${isActive('/config.htm')}>Configuration</a>
            <a ${isActive('/info.htm')}>System</a>
            <a onclick="restart()">Restart Software</a>
            <a onclick="reboot()">Reboot Raspberry Pi</a>
            <a onclick="shutdown()">Shutdown Raspberry Pi</a>
          </div>
        </div>
        <a href="/help.htm">Help</a>
      </div>
    </div>
  `;
  const innerDiv = div.querySelector('div');
  const body = document.querySelector('body')
  body.insertBefore(innerDiv, body.childNodes[0])
}
initializeNavBar();
