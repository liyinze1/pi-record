## Setup
Run 
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
``` 

put
```sudo /usr/sbin/alsactl --file /home/pi/pi-record/asound.state restore```
in
```sudo nano /etc/rc.local```

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
sudo cp vpn.service /etc/systemd/system/
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
```
sudo cp pi_record.service /etc/systemd/system/
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

