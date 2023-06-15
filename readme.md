## Setup
Run 
```
sudo bash setup-pi.sh
sudo bash setup-vpn.sh
sudo bash zerotier.sh
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
``` 

## VPN
### Zerotier
For the vpn between phone, pi and server, here I recommend [zerotier](https://www.zerotier.com/download/), and here is the [instruction](https://linuxhint.com/install-use-zerotier-raspberry-pi-virtual-network/) on
how to install it on a raspberry pi.

Make sure they can ping to each other.

Revise the ip address of the server and the network address on [config.yaml](./config.yaml)

### OpenVPN
```
sudo apt-get install openvpn unzip
```

```
sudo cp pi-vpn.service /etc/systemd/system/
sudo systemctl enable pi-vpn.service
sudo systemctl start pi-vpn.service
sudo systemctl status pi-vpn.service

sudo systemctl daemon-reload
sudo systemctl restart pi-vpn.service


sudo journalctl -f -u pi-vpn.service

```

## Local SSL Cerificate
see https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

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

