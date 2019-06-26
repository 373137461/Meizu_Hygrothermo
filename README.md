# Meizu_Hygrothermo


Home-assistant sensor platform for Meizu Meijia BT Hygrothermo temperature and humidity sensor.
![效果图1](img-folder/1.jpg?raw=true)
![效果图2](img-folder/2.jpg?raw=true)

Theory of all devices that can run python3 and support Bluetooth
According to feedback, the gateway can use
* PHICOMM N1
* Raspberry Pi full range

## Usage

To use, add the following to your `configuration.yaml` file:

```
sensor:
  - platform: meizu_hygrothermo
    name: ht #1
    host: 'xxx.xxx.xxx.xxx'
    mac: 'xx:xx:xx:xx:xx:xx'
    scan_interval: 60
```

- mac is your sensor Bluetooth MAC
- host is your Gateway Bluetooth MAC (I'm using a raspberry pi)
- mac and host is required.
- default "scan" interval is every 30 seconds.


## Determine the MAC address in the Gateway
- Copy "gateway.py" to your gateway device
- Please using python3 !!!

using hcitool:
```
$ sudo hcitool lescan
LE Scan ...
LE Scan ...
4C:65:A8:xx:xx:xx (unknown)
4C:65:A8:xx:xx:xx 1
[...]
```

using bluetoothctl:
```
$ sudo bluetoothctl 
[NEW] Controller xx:xx:xx:xx:xx:xx homeqube [default]
[bluetooth]# scan on
Discovery started
[CHG] Controller xx:xx:xx:xx:xx:xx Discovering: yes
[NEW] Device 4C:65:A8:xx:xx:xx 1
[bluetooth]# 
[bluetooth]# quit
```

look for 1 devices...

"1" you need to modify when pairing in the APP

- You can set the service or boot entry

