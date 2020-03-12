
sudo apt-get update -y
sudo apt-get dist-upgrade -y

sudo apt-get install i2c-tools

wget abyz.me.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
make
sudo make install
sudo pigpiod start

sudo apt-get install apache2 -y
sudo apt-get install php-sqlite3 -y
sudo apt-get install php -y

sudo apt-get install vim -y


