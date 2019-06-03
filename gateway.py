#!/usr/bin/env python3
# coding=utf-8
from socket import *
import sys
from bluepy.btle import UUID, Peripheral
HOST = '' 
PORT = 21567
BUFSIZ = 1024
ADDR=(HOST,PORT)
s = socket(AF_INET, SOCK_STREAM)
s.bind(ADDR)
s.listen(5)
while True:
	print('waiting for connecting...')
	c, addr = s.accept()
	print('..connected from:', addr)
	try:
		while True:
			data = c.recv(BUFSIZ)
			if not data:
				break
			print(data.decode(encoding='utf-8'))
			p = Peripheral(data.decode(encoding='utf-8'),"public")
			#services=p.getServices()
			chList = p.getCharacteristics()			 
			for ch in chList:
				if (str(ch.uuid)=="000016f2-0000-1000-8000-00805f9b34fb"):
					if (ch.supportsRead()):
						if(p.writeCharacteristic(ch.getHandle(),b'\x55\x03\x08\x11',True)):
							back=ch.read()
							humihex=back[6:8]
							temphex=back[4:6]
							temp10=int.from_bytes(temphex, byteorder='little')
							humi10=int.from_bytes(humihex, byteorder='little')
							temperature=float(temp10)/100.0
							humidity=float(humi10)/100.0
							if(p.writeCharacteristic(ch.getHandle(),b'\x55\x03\x01\x10',True)):
								back=ch.read()
								battery10=back[4]
								battery=float(battery10)/10.0
			p.disconnect()
			print(('{"temperature":"%s","humidity":"%s","battery":"%s"}' % (temperature,humidity,battery)))
			if ((int(temperature)==0 and int(humidity)==0) or int(temperature)>100 or int(humidity)>100):break
			c.send(('{"temperature":"%s","humidity":"%s","battery":"%s"}' % (temperature,humidity,battery)).encode())
			c.close()
	except Exception as ex:
		print("Unexpected error: {}".format(ex))
		c.close()
		p.disconnect()
s.close()