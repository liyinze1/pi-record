## Setup
<!-- Run 
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
``` 

put
```sudo /usr/sbin/alsactl --file /home/pi/pi-record/asound.state restore```
in
```sudo nano /etc/rc.local```
 -->


## Setup on Pi

### Install

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip ffmpeg git openvpn minicom -y

git clone https://github.com/liyinze1/pi-record.git

cd pi-record
git switch v2.3

sudo systemctl stop ModemManager
sudo systemctl disable ModemManager

python3 -m venv venv
source venv/bin/activate
pip install -r requirements/pi/requirements.txt
```

and turn on i2c
```
sudo raspi-config
```

### Zerotier
https://www.zerotier.com/download/

```bash
curl -s https://install.zerotier.com | sudo bash
```

### Modem

```bash
sudo minicom -D /dev/ttyUSB2

ATE1
AT+CUSBPIDSWITCH=9011,1,1
AT+CNMP=38
AT+CGDCONT=1,"IP","publicip.m2mmobi.be"
```

### Mic

Copy from https://github.com/filipmu/audio-recording-firmware-raspi-tlv320adc6140

in /boot/config.txt

`sudo nano /boot/firmware/config.txt`

```
dtparam=i2c_arm=on
dtparam=i2s=on
#dtparam=spi=on
dtoverlay=tlv320adcx140-overlay

# input pin to start the shut down sequence
dtoverlay=gpio-shutdown,gpio_pin=24,active_low=1,gpio_pull=up

# output pin to enable power source
dtoverlay=gpio-poweroff,gpiopin=26,active_low=1

```

`sudo raspi-config` to enble I2C

then put ``tlv320adcx140-overlay.dtbo`` in /overlays/overlay

`sudo cp tlv320adcx140-overlay.dtbo /boot/overlays`

### OpenVPN

```bash
sudo cp service/vpn.service /etc/systemd/system/
sudo systemctl enable vpn.service
sudo systemctl start vpn.service
sudo systemctl status vpn.service

sudo systemctl daemon-reload
sudo systemctl restart vpn.service


sudo journalctl -f -u vpn.service

```

## Local SSL Cerificate
see https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

## Service on pi
```bash
sudo cp service/pi_record.service /etc/systemd/system/
sudo systemctl enable pi_record.service
sudo systemctl start pi_record.service
sudo systemctl status pi_record.service

sudo systemctl stop pi_record.service
sudo systemctl daemon-reload
sudo systemctl restart pi_record.service


sudo journalctl -f -u pi_record.service

```
## Service on server
```
sudo cp server-record.service /etc/systemd/system/
sudo systemctl enable server-record.service
sudo systemctl start server-record.service
sudo systemctl status server-record.service

sudo systemctl daemon-reload
sudo systemctl restart server-record.service


sudo journalctl -f -u server-record.service
```

```
sudo nohup sudo python3 server.py &
ps aux | grep server.py
```

