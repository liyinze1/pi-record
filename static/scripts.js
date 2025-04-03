// variables
let vin = '';
let protocol = 'tcp';
let audio_name = '';

// check
function check_vin() {
    if (vin.length == 0) {
        update_message('Please scan a vin');
        return false;
    }
    return true;
}

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
    let msg = 'Device = ' + selected_device + '<br>VIN =' + vin + '<br>protocol = ' + protocol;
    if (data) {
        document.getElementById('message').innerHTML = msg + '<br>' + data;
    } else {
        document.getElementById('message').innerHTML = msg;
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
    deviceTableBody.innerHTML = ''; // Clear existing table rows
    vin = '';
    update_message('Getting device status, please wait...');


    const url = new URL('/devices', window.location.origin);
    url.searchParams.append('device', selected_device);

    fetch(url)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('connection to the server failed');
            }
        })
        .then(data => {
            update_message('');
            const row = document.createElement('tr');
            const deviceCell = document.createElement('td');
            const statusCell = document.createElement('td');

            deviceCell.textContent = data.status;
            statusCell.textContent = data.mode;

            document.getElementById('mode_message').innerHTML = data.mode_verbose;

            row.appendChild(deviceCell);
            row.appendChild(statusCell);
            deviceTableBody.appendChild(row);

            if (data == 'offline') {
                update_message('The device is offline, please wait for it to be online');
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
    if (decodedText.startsWith('test') || (decodedText.startsWith('WF') && decodedText.length == 17)) {
        vin = decodedText;
        update_message('VIN scanned, you can start recording');
        html5QrCode.stop().then((ignore) => {
            console.log('stopped')
        }).catch((err) => {});
        document.getElementById('record_tab_button').click();
    }
}
const config = { fps: 10, qrbox: qrboxFunction };

// record
function startRecording() {
    if (!check_device_vin()) {
        return;
    }
    update_message('trying to start recording...');
    fetch('/record', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vin: vin, device: selected_device, protocol: protocol})
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
    update_message('trying to stop recording');
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

        document.getElementById('label_tab_button').click();
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
            update_message('connection to the server failed');
            throw new Error('connection to the server failed');
        }
    })
    .then(data => {
        console.log(data);
        update_message('ok, please scan a new car');
        document.getElementById('scan_tab_button').click();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// protocol

function select_protocol(option) {
    if (option == 0) {
        protocol = 'rtp';
    } else if (option == 1) {
        protocol = 'tcp';
    }
    update_message('Protocol selected:'+ protocol);
}


// Check Audios
function fetch_audio() {
    document.getElementById('audio_source').src = '';
    document.getElementById('audio_box').load();
    if (!check_vin()) {
        return;
    }
    update_message('trying to fetch the audio...');
    fetch('/get-audio/' + vin, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error('connection to the server failed');
        }
    })
    .then(data => {
        if (data.length === 0) {
            update_message('No audio found for this VIN');
            document.getElementById('audio_source').src = '';
            return;
        } else {
            console.log(data);
            update_message("found an audio, name: " + data);
            audio_name = data;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function play() {
    if (!check_vin()) {
        return;
    }
    if (audio_name.length == 0) {
        update_message('No audio to play, please check at first');
        return;
    }
    document.getElementById('audio_source').src = "play/" + audio_name;
    document.getElementById('audio_box').load();
}

function download() {
    if (!check_vin()) {
        return;
    }
    if (audio_name.length == 0) {
        update_message('No audio to download, please check at first');
        return;
    }
    window.open('/play/' + audio_name)
}

function delete_audio() {
    if (!check_vin()) {
        return;
    }
    if (audio_name.length == 0) {
        update_message('No audio to delete, please check at first');
        return;
    }

    if (!confirm(`Are you sure you want to delete ${audio_name}?`)) {
        return;
    }

    fetch('/delete/' + audio_name, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            update_message('deleted!');
            document.getElementById('audio_source').src = '';
            document.getElementById('audio_box').load();
            audio_name = '';
        } else {
            throw new Error('connection to the server failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// Default to tab Device on page load
//document.getElementById('tabDevice').style.display = 'block';
document.addEventListener('DOMContentLoaded', fetchDevices);
