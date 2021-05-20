
sudo apt-get update -y
sudo apt-get dist-upgrade -y

sudo apt-get install i2c-tools -y
sudo apt-get install apache2 -y
sudo apt-get install php-sqlite3 -y
sudo apt-get install php -y

sudo apt-get install vim

wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
