sudo apt-get install openvpn unzip
sudo cp pi-vpn.service /etc/systemd/system/
sudo systemctl enable pi-vpn.service
sudo systemctl start pi-vpn.service
sudo systemctl status pi-vpn.service
sudo chmod 777 /home/pi/vpn.ovpn