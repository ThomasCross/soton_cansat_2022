from digi.xbee.devices import XBeeDevice

device = XBeeDevice("/dev/ttyS0", 9600)
device.open()
device.send_data_broadcast("Hello XBee World!")

print("Reading...\n")

while True:
	data = device.read_data()
	if(data != None):
		if(data.data == b"secret"):
			device.send_data_broadcast("shhhh")
		print(data.remote_device,"\n",data.data)
		print("\n")
		remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string(
		"0013A20041CF05CC"))

		# Send data using the remote object.
		xbee.send_data_async(remote, "Message received!")
		device.close()
