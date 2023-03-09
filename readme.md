## Setup
Run 
```
python3 -m venv ford-venv
source ford-venv/bin/activate
pip3 install -r requirements.txt
``` 
on both server and pi to install python dependencies

It's also required a package called [FFmpeg](https://ffmpeg.org/) on both sides to send and receive audio stream.

Try ```sudo apt install -y ffmpeg``` or, ```brew install ffmpeg``` or [manually download it](https://ffmpeg.org/download.html)

## VPN
For the vpn between phone, pi and server, here I recommend [zerotier](https://www.zerotier.com/download/), and here is the [instruction](https://linuxhint.com/install-use-zerotier-raspberry-pi-virtual-network/) on
how to install it on a raspberry pi.

Make sure they can ping to each other.

Revise the ip address of the server and the network address on [config.yaml](./config.yaml)

```
sudo cp server-record.service /etc/systemd/system/
sudo systemctl enable vpn.service
sudo systemctl start vpn.service
sudo systemctl status vpn.service

sudo systemctl daemon-reload
sudo systemctl restart vpn.service


sudo journalctl -f -u vpn.service

```

## Local SSL Cerificate
see https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

## Service on pi
```
sudo cp pi-record.service /etc/systemd/system/
sudo systemctl enable pi-record.service
sudo systemctl start pi-record.service
sudo systemctl status pi-record.service

sudo systemctl daemon-reload
sudo systemctl restart  pi-record.service


sudo journalctl -f -u pi-record.service

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

