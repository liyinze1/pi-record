## 0. Setup
### 0.1 Packages
Run ```pip3 install -r requirements.txt``` on both server and pi to install python dependencies

It's also required a package called [FFmpeg](https://ffmpeg.org/) on both sides to send and receive audio stream.

Try ```sudo apt install -y ffmpeg``` or, ```brew install ffmpeg``` or [manually download it](https://ffmpeg.org/download.html)

### 0.2 VPN
For the vpn between phone, pi and server, here I recommend [zerotier](https://www.zerotier.com/download/), and here is the [instruction](https://linuxhint.com/install-use-zerotier-raspberry-pi-virtual-network/) on
how to install it on a raspberry pi.

Make sure they can ping to each other.

Revise the ip address of the server and the network address on [config.yaml](./config.yaml)

### 0.3 Tethering
Install zerotier on the phone and share Internet to the pi by hotspot.

## 1. Run
Run ```cd pi-record``` and ```sudo -E python3 pi.py``` on the pi, and ```python3 server.py``` on the server

## 2. Record
Open ```https://[pi's ip address]:8000``` on the phone, and make sure it's https


## Local SSL Cerificate
see https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

## Service
```
sudo cp pi-record.service /etc/systemd/system/
sudo systemctl enable pi-record.service
sudo systemctl start pi-record.service
sudo systemctl status pi-record.service

sudo systemctl daemon-reload
sudo systemctl restart  pi-record.service


sudo journalctl -f -u  pi-record.service

```