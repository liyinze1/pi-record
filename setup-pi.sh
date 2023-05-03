sudo apt install -y ffmpeg
sudo apt install -y python3-pip
pip3 install -r requirements/pi/requirements.txt
sudo cp pi-record.service /etc/systemd/system/
sudo systemctl enable pi-record.service
sudo systemctl start pi-record.service
sudo systemctl status pi-record.service
mkdir ./audio
sudo chmod 777 -r .
sudo chmod 777 .