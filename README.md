# fancontrol-hddtemp

This script is used to control case fans depending on the hard disk temperature.
In addition, the cpu temperature is evaluated (from above the threshold temperature) in order to improve 
the air flow in the housing (e. g. front fan -> hdd -> chipset -> cpu -> rear fan) towards the cpu.

## Installing fancontrol-hddtemp

```
sudo -i
mkdir /git
cd /git
git clone https://github.com/Floyddotnet/fancontrol-hddtemp

ln -s /git/fancontrol-hddtemp/fancontrol-hddtemp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable fancontrol-hddtemp.service
systemctl start fancontrol-hddtemp.service
```
