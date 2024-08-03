// variables
let vin = '';
let selected_device = '';

// check
function check_device_vin() {
    if (selected_device.length == 0) {
        announce_message('Please select a device');
        return false;
    }
    if (vin.length == 0) {
        update_message('Please scan a vin');
        return false;
    }
    return true;
}


// tab switch
function openTab(event, tabId) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName('tab-content');
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = 'none';
        tabcontent[i].classList.remove('active');
    }
    tablinks = document.querySelectorAll('nav a');
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove('active');
    }
    document.getElementById(tabId).style.display = 'block';
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// update message
function update_message(data) {
    if (data) {
        document.getElementById('message').innerHTML = 'selected device = ' + selected_device + '<br>selected VIN =' + vin + '<br>' + data;
    } else {
        document.getElementById('message').innerHTML = 'selected device = ' + selected_device + '<br>selected VIN =' + vin;
    }
}

function announce_message(data) {
    document.getElementById('message').innerHTML = data;
}

// fetch devices
function device_tab_click(event, tabId) {
    openTab(event, tabId);
    fetchDevices();
}

function fetchDevices() {
    const deviceTableBody = document.getElementById('device-table-body');
    const deviceButtonsContainer = document.getElementById('device-buttons');
    deviceTableBody.innerHTML = ''; // Clear existing table rows
    deviceButtonsContainer.innerHTML = ''; // Clear existing buttons
    vin = '';
    selected_device = '';
    announce_message('Getting device list, please wait...');

    fetch('/devices')
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('connection to the server failed');
            }
        })
        .then(devices => {
            announce_message('Please select a device')
            for (const [device, status] of Object.entries(devices)) {
                const row = document.createElement('tr');
                const deviceCell = document.createElement('td');
                const statusCell = document.createElement('td');

                deviceCell.textContent = device;
                statusCell.textContent = status;

                row.appendChild(deviceCell);
                row.appendChild(statusCell);
                deviceTableBody.appendChild(row);

                if (status != 'offline') {
                    const button = document.createElement('button');
                    button.className = 'blue';
                    button.textContent = device;
                    button.onclick = () => {
                        selected_device = device;
                        update_message('Please scan the VIN number');
                        document.getElementById('scan_tab_button').click();
                    };
                    deviceButtonsContainer.appendChild(button);
                }   
            }
        })
        .catch(error => {
            announce_message('Error', error)
            console.error('Error', error);
        });
}

// scan QR code
function scan_vin() {
    console.log('scan vin')
    html5QrCode.start({ facingMode: 'environment' }, config, qrCodeSuccessCallback);
}
let qrboxFunction = function (viewfinderWidth, viewfinderHeight) {
    let minEdgePercentage = 0.7;
    let minEdgeSize = Math.min(viewfinderWidth, viewfinderHeight);
    let qrboxSize = Math.floor(minEdgeSize * minEdgePercentage);
    return {
        width: qrboxSize,
        height: qrboxSize
    };
};
const html5QrCode = new Html5Qrcode('qr-reader', { formatsToSupport: [ Html5QrcodeSupportedFormats.QR_CODE] });
const qrCodeSuccessCallback = (decodedText, decodedResult) => {
    console.log(`Code scanned = ${decodedText}`, decodedResult);
    if (decodedText.startsWith('WF') && decodedText.length == 17) {
        update_message('VIN scanned, you can start recording')
        document.getElementById('record_tab_button').click();
    }
}
const config = { fps: 10, qrbox: qrboxFunction };

// record
function startRecording() {
    if (!check_device_vin()) {
        return;
    }
    fetch('/record', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vin: vin, device: selected_device })
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error('connection to the server failed');
        }
    })
    .then(data => {
        console.log(data);
        update_message(data);
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function stopRecording() {
    if (!check_device_vin()) {
        return;
    }
    fetch('/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vin: vin, device: selected_device })
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error('connection to the server failed');
        }
    })
    .then(data => {
        console.log(data);
        update_message(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// label
function label(option) {
    if (!check_device_vin()) {
        return;
    }
    fetch('/label', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vin: vin, device: selected_device, label: option})
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error('connection to the server failed');
        }
    })
    .then(data => {
        console.log(data);
        update_message(data);
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Default to tab Device on page load
//document.getElementById('tabDevice').style.display = 'block';
document.addEventListener('DOMContentLoaded', fetchDevices);
