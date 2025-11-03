import argparse
from pymodbus.client import ModbusTcpClient
import struct

#Get the coil value at the specified address | Given location %QX0.0-0.4 coil_address should be %QX0.coil_address
def get_coil(client, coil_address):
	return client.read_coils(coil_address, device_id=1).bits[0]


#Set the coil value at the given address
#new_value should be either (True or False)
def set_coil(client, coil_address, new_value):
	return not client.write_coil(coil_address, new_value, device_id=1).isError()


#Get the float value in a register - 32bit 
def get_32bit_register(client, starting_address):

	#Uses the given address and reads 2 registers to get the 16bit numbers
	result = client.read_holding_registers(address=starting_address, count=2, device_id=1)

	#if there is no error then continue
	if not result.isError():
		print(result.registers)

		#decode the two 16bit numbers to a big endian 32bit number
		float_value = client.convert_from_registers(
			result.registers,
			data_type=client.DATATYPE.FLOAT32,
			word_order="little"
		)

		#return the value
		return float_value
	else:
		return None


def number_to_two_16bit(number):
	if isinstance(number, int):
		#convert the int to a float value
		float_value = struct.unpack('f', struct.pack('f', number))[0]
	else:
		float_value = number

	#convert the float to two int16 values
	int_rep = struct.unpack('!I', struct.pack('!f', float_value))[0]
	high_bits = int_rep >> 16
	low_bits = int_rep & 0xFFFF
	return [low_bits, high_bits]


#Set the float value at the given register address
def set_32bit_register(client, starting_address, new_int_value):
	#Convert the new_int_value to two 16bit numbers
	new_values = number_to_two_16bit(new_int_value)

	#Get the result of the changing the first register
	result = client.write_register(address=starting_address, value=new_values[0], device_id=1)

	#Get the result of the chaning the second register
	result_two = client.write_register(address=starting_address+1, value=new_values[1], device_id=1)
	return not (result.isError() and result.isError())

#Get the value of a 16bit register from the address
def get_16bit_register(client, address):
	#Request the encoded register value
	result = client.read_holding_registers(address=address, count=1, device_id=1)

	if not result.isError():
		#Decode the register value if there is no error
		int_value = client.convert_from_registers(
			result.registers,
			data_type=client.DATATYPE.INT16,
			word_order="little"
		)
		return int_value
	else:
		return None

#Set the value of a 16bit register from the address
def set_16bit_register(client, address, new_int_value):
	#Set the value and return if the result is an error
	result = client.write_register(address=address, value=new_int_value, device_id=1)
	return not result.isError()

def return_bool_val(value):
	if value == 0:
		return False
	elif value == 1:
		return True
	else:
		return None

def client():
	#arg parser
	parser = argparse.ArgumentParser(description="Modbus Interaction from the CLI to Read/Write to Coils and Registers")

	#Add the read and write options, and allow user to only choose one.
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-r", "--read", action="store_true", help="Read from the given modbus address")
	group.add_argument("-w", "--write", action="store_true", help="Write to a given modbus address")

	#Add the IP and Port options. The IP is required, but port has a default value and is not
	parser.add_argument("--ip", action="store", help="The IP address of the ModBus Device", required=True)
	parser.add_argument("--port", action="store", default=502, help="The port of the the ModBus Service", required=False)

	#Add the address value. This is required to identify the correct register/coil
	parser.add_argument("-a", "--address", action="store", help="Target address on the ModBus Device")

	#Add the register types, these are required but exclusive to not confuse the program.
	types = parser.add_mutually_exclusive_group(required=True)
	types.add_argument("-i", "--integer", action="store_true", help="Select a 16bit Integer as the target at the address")
	types.add_argument("-f", "--float", action="store_true", help="Select a 32bit Float as the target at the address")
	types.add_argument("-c", "--coil", action="store_true", help="Select a coil as the target at the address")

	#Add the value option, this is only necessary if doing a write operation.
	parser.add_argument("-v", "--value", action="store", help="The new value to store at the given address")

	#Get the args
	args = parser.parse_args()

	#Check if the value arg is set when trying to write
	if args.write and args.value is None:
		parser.error("-w requires -v arguement")

	#Check that the value argument is not set when trying to read
	if args.read and args.value is not None:
		parser.error("-r does not accept the -v argument")

	#Check that the value is only 0, or 1 when writing to a coil.
	#This check is being done with the value still as a string to mitigate a ValueError if I int the value and its not valid.
	if args.write and args.coil and args.value not in ["0", "1"]:
		parser.error("-c requires -v is only 1 (true) or 0 (false)")

	#If writing and the target is a float, then confirm that the given value can be converted to a float
	if args.write and args.float:
		try:
			float(args.value)
		except ValueError:
			parser.error("-v value is not a valid float")

	#If writing and the target is an integer, then confirm that the given value can be converted to an int
	if args.write and args.integer:
		try:
			int(args.value)
		except ValueError:
			parser.error("-v value is not a valid integer")

	#Connect to Modbus TCP Server on PLC
	client = ModbusTcpClient(f"{args.ip}",port=int(args.port))
	client.connect()

	#Logic for is -c is selected
	if args.coil:
		#Check if reading
		if args.read:
			#Do the read operation
			operation = get_coil(client, int(args.address))
			#Check the read was successful, if not then report to user the failure
			if operation != None:
				print(f"Success: {args.ip}:{args.port} Coil {args.address} = {operation}")
			else:
				print(f"Error: Unable to Read Value from coil {args.address}")

		#Check if writing
		if args.write:
			#Get the original value before doing the set
			old_val = get_coil(client, int(args.address))
			#Complete the write operation
			operation = set_coil(client, int(args.address), int(args.value))
			#Check if the operating was successful if not alert the user to the error.
			if operation:
				print(f"Success: {args.ip}:{args.port} Coil {args.address} changed from {old_val} to {return_bool_val(int(args.value))}")
			else:
				print(f"Error: Unable to set value")


	#Logic for if -f is selection
	if args.float:
		#Check if reading
		if args.read:
			#Do the read operation
			operation = get_32bit_register(client, int(args.address))
			#Confirm the read was successful, and output the results. If the read failed then alert the user
			if operation != None:
				print(f"Success: {args.ip}:{args.port} Register {args.address}-{int(args.address)+1} = {operation}")
			else:
				print(f"Error: Reading {args.ip}:{args.port} Register {args.address}")

		#Check if writing
		if args.write:
			#Get the original value before doing the write
			old_val = get_32bit_register(client, int(args.address))
			#Complete the write operation
			operation = set_32bit_register(client, int(args.address), float(args.value))
			#If successful let the user know of the change, if unsuccessful then alert them
			if operation:
				print(f"Success: {args.ip}:{args.port} Register {args.address}-{int(args.address)+1} changed from {old_val} to {args.value}")
			else:
				print(f"Error: Unable to set value")


	#Logic for if -i is selection
	if args.integer:
		#Check if reading
		if args.read:
			#Do the read operation
			operation = get_16bit_register(client, int(args.address))
			#If the read was successful then let the user know, otherwise throw an error
			if operation != None:
				print(f"{args.ip}:{args.port} Register {args.address} = {operation}")
			else:
				print(f"Error: Unable to Read {args.ip}:{args.port} Register {args.address}")

		#Check if writing
		if args.write:
			#Get the original value before doing the write
			old_val = get_16bit_register(client, int(args.address))
			#Complete the write operation
			operation = set_16bit_register(client, int(args.address), int(args.value))
			#If successful let the user know of the change, fi unsuccessful then alert them.
			if operation:
				print(f"Success: {args.ip}:{args.port} Register {args.address} changed from {old_val} to {args.value}")
			else:
				print(f"Error: Unable to set value")

if __name__ == "__main__":
	client()
