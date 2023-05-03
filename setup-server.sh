sudo apt install -y python3-pip
pip3 install -r requirements/pi/requirements.txt
sudo cp server-record.service /etc/systemd/system/
sudo systemctl enable server-record.service
sudo systemctl start server-record.service
sudo systemctl status server-record.service
mkdir ./audio
sudo chmod 777 -r .
sudo chmod 777 .