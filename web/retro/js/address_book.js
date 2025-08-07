const scrollingDiv = document.getElementById('scrollingDiv');
const tableRowTemplate = document.getElementById('tableRow');
const tableBody = document.getElementById('tableBody');
const standardCounts = document.querySelector('.standard-count');
const fanCounts = document.querySelector('.fan-count');

addresses = [];
symbols = [];

fetchData();

function updateIp(ip) {
  const parts = ip.split('.').map(Number);

  return parts.join('·');
}

function hash(str) {
  let hash = 0,
    i,
    chr;
  if (str.length === 0) return hash;
  for (i = 0; i < str.length; i++) {
    chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
}

const randomText = ['E<br>M', 'P<br>Q', 'G<br>X', 'T<br>V', 'I<br>X'];

async function fetchData() {
  try {
    const response = await fetch('/stargate/get/address_book?type=all');
    const data = await response.json();
    standardCounts.textContent = data.summary.standard;
    fanCounts.textContent = data.summary.fan;
    addresses = Object.values(data['address_book']);

    const responseSymbols = await fetch('/stargate/get/symbols_all');
    symbols = await responseSymbols.json();

    parseData();
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

function parseData() {
  addresses.forEach(address => {
    const aTag = document.createElement('a');
    aTag.setAttribute('href', `/stargate/dial?address=${address.gate_address.join('-')}`);
    address.htmlData = aTag;

    const newRow = tableRowTemplate.cloneNode(true);
    aTag.appendChild(newRow);
    newRow.removeAttribute('id');
    newRow.classList.remove('hidden');

    let keyboardAddress = '';
    let hasUnknownGlyph = false;

    address['gate_address'].forEach((glyph, i) => {
      const symbol = symbols.find(x => x['index'] === glyph);

      if (!symbol || symbol['keyboard_mapping'] === false) {
        keyboardAddress += '?';
        hasUnknownGlyph = true;
      } else {
        keyboardAddress += symbol['keyboard_mapping'];
      }

      if (i < 7) {
        newRow.querySelector(`.glyph-name-${i + 1}`).textContent =
          symbol?.['name'] ?? 'Unknown';

        const imgElement = newRow.querySelector(`.glyph-${i + 1}`);
        imgElement.src = ''; // Empty it temporarily
        imgElement.src = '..' + symbol?.['imageSrc']; // Set it again to force a reload
      }
    });

    const randomNumber = Math.floor(Math.random() * 5);
    newRow.querySelector('.small-box').innerHTML = randomText[randomNumber];

    newRow.querySelector(
      `.info-name`,
    ).textContent = `${address['name']} # ${keyboardAddress}8`;

    if (
      address['is_black_hole'] ||
      hasUnknownGlyph ||
      address['gate_address'].length > 6
    ) {
      newRow.classList.add('danger');
    }

    if (address['type'] === 'fan') {
      newRow.classList.add('fan');
      newRow
        .querySelector('.info-type')
        .querySelectorAll('span')[1].textContent = 'Fan';
    } else {
      newRow
        .querySelector('.info-type')
        .querySelectorAll('span')[1].textContent = 'Standard';
    }

    if (address['is_gate_online'] === '0') {
      newRow.classList.add('offline');
      newRow.querySelector('.status').querySelectorAll('span')[1].textContent =
        'Offline';
    } else {
      newRow.querySelector('.status').querySelectorAll('span')[1].textContent =
        'Online';
    }

    if (address['ip_address']) {
      newRow
        .querySelector('.info-coord')
        .querySelectorAll('span')[1].textContent = updateIp(
        address['ip_address'],
      );
    } else {
      newRow
        .querySelector('.info-coord')
        .querySelectorAll('span')[0].textContent = '';
      newRow
        .querySelector('.info-coord')
        .querySelectorAll('span')[1].textContent = '';
    }

    newRow
      .querySelector('.info-const')
      .querySelectorAll('span')[1].textContent = Math.abs(
      hash(JSON.stringify(address)),
    );

    newRow
      .querySelector('.info-ref')
      .querySelectorAll('span')[1].textContent = `${Math.floor(
      Math.random() * 999,
    )
      .toString()
      .padStart(3, '0')}x${Math.floor(Math.random() * 9999)}`;

    newRow.querySelector('.info-a').innerHTML = generatePlanetData();

    tableBody.appendChild(aTag);
  });

  sortData('name');
}

function sortData(sortProperty) {
  addresses.sort((a, b) => a.name.localeCompare(b.name));

  if (sortProperty === 'type') {
    addresses.sort((a, b) => a.type.localeCompare(b.type));
  } else if (sortProperty === 'status') {
    addresses.sort(
      (a, b) =>
        a.type.localeCompare(b.type) ||
        (b.is_gate_online ?? '0').localeCompare(a.is_gate_online ?? '0'),
    );
  } else if (sortProperty === 'glyph') {
    addresses.sort((a, b) =>
      a.gate_address
        .map(x => x.toString().padStart(3, '0'))
        .join('')
        .localeCompare(
          b.gate_address.map(x => x.toString().padStart(3, '0')).join(''),
        ),
    );
  }

  addresses.forEach(address => {
    tableBody.appendChild(address.htmlData);
  });

  tableBody.scrollTo(0, 0);
}

const labelOptions = {
  Mission: [
    'Complete',
    'Pending',
    'Active',
    'Failed',
    'Aborted',
    'Ongoing',
    'Incomplete',
    'Success',
    'Recon',
    'Contact',
    'Delayed',
  ],
  Survey: [
    'Complete',
    'Partial',
    'In progress',
    'Failed',
    'Limited scan',
    'Area mapped',
    'Outpost found',
    'No data',
    'Hazard zones',
    'Energy spike',
    'Inconclusive',
  ],
  Terrain: [
    'Mixed',
    'Plateau',
    'Valley',
    'Forest',
    'Desert',
    'Jungle',
    'Glacier',
    'Marsh',
    'Tundra',
    'Oasis',
    'Ocean',
  ],
  Life: ['Detected', 'Unknown', 'Extinct'],
  Team: [
    'Deployed',
    'Returned',
    'Missing',
    'Awaiting evac',
    'En route',
    'No contact',
    'In orbit',
    'Standing by',
    'Request backup',
    'Safe',
  ],
  Tech: [
    'Unknown',
    'Primitive',
    'Advanced',
    'Inactive',
    'Damaged',
    'Non-native',
    'Functional',
    'No signs',
  ],
  Scan: [
    'Normal',
    'Stable',
    'Interference',
    'Disturbance',
    'Power reading',
    'Active signals',
    'Structural mass',
    'Unknown field',
    'Signal trace',
    'Bio signature',
  ],
  Air: [
    'Breathable',
    'Thin',
    'Toxic',
    'Heavy gases',
    'Oxygen rich',
    'Unstable',
    'Safe level',
    'Mask required',
    'Contaminated',
    'No trace',
  ],
  'O2 Level': [
    '19%',
    '20%',
    '21%',
    '22%',
    '23%',
    '18%',
    '17% (Low)',
    '24%',
    '16% (Risk)',
    '25%',
  ],
  Temp: [
    '5°C',
    '12°C',
    '18°C',
    '22°C',
    '27°C',
    '30°C',
    '-5°C (Cold)',
    '35°C (Hot)',
    '0°C',
    '15°C',
  ],
  Gravity: [
    '0.8G',
    '0.9G',
    '1.0G',
    '1.1G',
    '1.2G',
    '0.95G',
    '1.05G',
    '0.7G (Low)',
    '1.3G (High)',
    '1.15G',
  ],
  Rad: [
    '0.1 mSv/h',
    '0.2 mSv/h',
    '0.05 mSv/h',
    '0.3 mSv/h',
    '0.4 mSv/h',
    '0.0 mSv/h',
    '0.6 mSv/h',
    '0.9 mSv/h (Caution)',
    '0.8 mSv/h',
    '0.25 mSv/h',
  ],
  Atm: [
    '0.9 bar',
    '1.0 bar',
    '1.1 bar',
    '1.2 bar',
    '0.95 bar',
    '1.05 bar',
    '0.8 bar (Thin)',
    '1.3 bar (Dense)',
    '0.85 bar',
    '1.15 bar',
  ],
  Seismic: [
    'None',
    'Low',
    'Minor tremors',
    'Stable',
    '0.3 Hz',
    '0.5 Hz',
    'Microquakes',
    '0.1 Hz',
    'Irregular',
    '0.0 Hz',
  ],
  'Mag Field': [
    '45 μT',
    '50 μT',
    '38 μT',
    '60 μT',
    '42 μT',
    '55 μT',
    '48 μT',
    '35 μT',
    '65 μT',
    '40 μT',
  ],
  Wind: [
    '0 km/h',
    '5 km/h',
    '12 km/h',
    '8 km/h',
    '20 km/h',
    '15 km/h',
    '25 km/h (Gusty)',
    '3 km/h',
    '10 km/h',
    '18 km/h',
  ],
};
const notes = [
  'No anomalies',
  'Culture noted',
  'Further Review',
  'Awaiting orders',
  'Culture observed',
  'Gate unstable',
  'Threat detected',
  'Artifacts logged',
  'Scan incomplete',
  'Base camp set',
  'Unknown energy',
  'Transmission lost',
  'Possible ruins',
  'Minimal contact',
  'Team under review',
  'Quarantine zone',
  'Language unknown',
  'Debris analyzed',
  'Unreadable data',
  'Life signs low',
  'Survey incomplete',
  'Hostile encounter',
  'Pre-warp civ',
  'Tech interference',
  'Records missing',
  'Sensors limited',
  'Limited access',
  'Return scheduled',
];

// Generates 3 random attributes from the dict of labelOptions
// Small chance of adding a Notes section
// Even smaller chance of redacting the value
function generatePlanetData() {
  let toReturn = [];
  let options = Object.keys(labelOptions);
  for (let i = 0; i < 3; i++) {
    const index = Math.floor(Math.random() * options.length);
    const entry = options.splice(index, 1);
    const optionIndex = Math.floor(Math.random() * labelOptions[entry].length);
    const redacted = Math.random() < 0.02;
    if (redacted) {
      toReturn.push(`${entry}: *****`);
    } else {
      toReturn.push(`${entry}: ${labelOptions[entry][optionIndex]}`);
    }
  }
  if (Math.random() < 0.15) {
    // Add Note
    const noteIndex = Math.floor(Math.random() * notes.length);
    toReturn.push(`Note: ${notes[noteIndex]}`);
  }

  return toReturn.join('<br>');
}
