import argparse
from pymodbus.client import ModbusTcpClient
import struct

"""
 ------------- HELPER FUNCTIONS -------------

 - number_to_two_16bit(number, data_type, client)
	-> number -- number to convert to 16bit format
	-> data_type -- datatype constant from pymodbus the number value should be (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	-> client -- pymodbus client object (only needed to access data_type constants)
	RETURN: [high_bits, low_bits]; list with highest 16bits first, and lowest 16bits last

 - number_to_four_16bit(number, data_type, client)
	-> number -- number to conver to 16bit format
	-> data_type -- datatype constant from pymodbus the number value should be (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	-> client -- pymodbus client object (only needed to access data_type constants)
	RETURN: [part1, part2, part3, part4]; list with highest 16bits first, and lowest 16bits last
"""

#Convert a 32bit number into two 16bit numbers
#To send to the individual registers making up a 32bit number
def number_to_two_16bit(number, data_type, client):
	#Check the datatype being saved to pack it correctly
	if data_type == client.DATATYPE.FLOAT32:
		#conver the int to a float value
		packed_value = struct.pack('>f', float(number))
	elif data_type == client.DATATYPE.UINT32:
		packed_value = struct.pack('>I', number)
	elif data_type == client.DATATYPE.INT32:
		packed_value = struct.pack('>i', number)

	#get the high, and low values and return to calling function
	high_bits, low_bits = struct.unpack('>HH', packed_value)
	return [high_bits, low_bits]

#Convert a 64bit number into four 16bit numbers
#To send to the individual registers making up a 64 bit number
def number_to_four_16bit(number, data_type, client):
	if data_type == client.DATATYPE.FLOAT64:
		#Convert the int to a 64-bit float
		packed_value = struct.pack('>d', float(number))
	elif data_type == client.DATATYPE.UINT64:
		packed_value = struct.pack('>Q', number)
	elif data_type == client.DATATYPE.INT64:
		packed_value = struct.pack('>q', number)

	#get all the values and return to the calling function
	part1, part2, part3, part4 = struct.unpack('>HHHH', packed_value)

	return [part1, part2, part3, part4]

"""
  ------------- CLIENT FUNCTIONS  -------------
 - get_coil(client, coil_address)
	-> client -- pymodbus client object
	-> coil_address -- physical address of the coil
	RETURN: recieved value from coil

 - set_coil(client, coil_address, new_value)
	-> client -- pymodbus client object
	-> coil_address -- physical address of the coil
	-> new_value -- new binary value to write to the coil (0 or 1)
	RETURN: boolean 1 if successful write, 0 if failed write

 - get_64bit_register(client, starting_address, data_type)
	-> client -- pymodbus client object
	-> starting_address -- physical address of the first register in the set of 4 required
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	RETURN: recieved value from register

 - set_64bit_register(client, starting_address, new_value, data_type)
	-> client -- pymodbus client object
	-> starting_address -- physical address of the first register in the set of 4 required
	-> new_value -- new integer or float value to be saved in the 64bit Register
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	RETURN: boolean 1 if successful write, 0 if failed write

 - get_32bit_register(client, starting_address, data_type)
	-> client -- pymodbus client object
	-> starting_address -- physical address of the first register in the set of 4 required
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	RETURN: recieved value from register

- set_32bit_register(client, starting_address, new_value, data_type)
	-> client -- pymodbus client object
	-> starting_address -- physical address of the first register in the set of 4 required
	-> new_value -- new integer or float value to be saved in the 32bit Register
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	RETURN: boolean 1 if successful write, 0 if failed write

 - get_16bit_register(client, starting_address, data_type)
	-> client -- pymodbus client object
	-> starting_address -- physical address of the first register in the set of 4 required
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	RETURN: recieved value from register

- set_16bit_register(client, starting_address, new_value, data_type)
	-> client -- pymodbus client object
	-> starting_address -- physical address of the first register in the set of 4 required
	-> new_value -- new integer or float value to be saved in the 16bit Register
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)
	RETURN: boolean 1 if successful write, 0 if failed write

"""

#Get the coil value at the specified address | Given location %QX0.0-0.4 coil_address should be %QX0.coil_address
def get_coil(client, coil_address):
	return client.read_coils(coil_address, device_id=1).bits[0]


#Set the coil value at the given address
#new_value should be either (True or False)
def set_coil(client, coil_address, new_value):
	return not client.write_coil(coil_address, new_value, device_id=1).isError()


#Get the unsigned int value in a register - 64bit
def get_64bit_register(client, starting_address, data_type):

	#Uses the given address and reads 4 registers to get the 16bit numbers
	result = client.read_holding_registers(address=starting_address, count=4, device_id=1)

	#if there is no error then continue
	if not result.isError():

		#decode the two 16bit numbers to a big endian 64bit number
		register_value = client.convert_from_registers(
			result.registers,
			data_type=data_type,
			word_order="big"
		)

		#return the value
		return register_value
	else:
		return None

#Set the value of the given 64bit register
def set_64bit_register(client, starting_address, new_value, data_type):
	#Convert the new_value to four 16bit numbers
	new_values = number_to_four_16bit(new_value, data_type, client)

	#Get the result of the changing the first register
	result = client.write_register(address=starting_address, value=new_values[0], device_id=1)

	#Get the result of changing the second register
	result_two = client.write_register(address=starting_address+1, value=new_values[1], device_id=1)

	#Get the result of changing the third register
	result_three = client.write_register(address=starting_address+2, value=new_values[2], device_id=1)

	#Get the result of changing the fourth register
	result_four = client.write_register(address=starting_address+3, value=new_values[3], device_id=1)

	#Check that all were successful
	return not(result.isError() and result_two.isError() and result_three.isError() and result_four.isError())


#Get the value in a register - 32bit
def get_32bit_register(client, starting_address, data_type):

	#Uses the given address and reads 2 registers to get the 16bit numbers
	result = client.read_holding_registers(address=starting_address, count=2, device_id=1)

	#if there is no error then continue
	if not result.isError():

		#decode the two 16bit numbers to a big endian 32bit number
		register_value = client.convert_from_registers(
			result.registers,
			data_type=data_type,
			word_order="big"
		)

		#return the value
		return register_value
	else:
		return None

#Set the float value at the given register address
def set_32bit_register(client, starting_address, new_value, data_type):
	#Convert the new_int_value to two 16bit numbers
	new_values = number_to_two_16bit(new_value, data_type, client)

	#Get the result of the changing the first register
	result = client.write_register(address=starting_address, value=new_values[0], device_id=1)

	#Get the result of the chaning the second register
	result_two = client.write_register(address=starting_address+1, value=new_values[1], device_id=1)
	return not (result.isError() and result_two.isError())

#Get the value of a 16bit register from the address
def get_16bit_register(client, address, data_type):
	#Request the encoded register value
	result = client.read_holding_registers(address=address, count=1, device_id=1)

	if not result.isError():
		#Decode the register value if there is no error
		int_value = client.convert_from_registers(
			result.registers,
			data_type=data_type,
			word_order="big"
		)
		return int_value
	else:
		return None

#Set the value of a 16bit register from the address
def set_16bit_register(client, address, new_value, data_type):
	#Set the value and return if the result is an error
	result = client.write_register(address=address, value=new_value, device_id=1)
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

	#Add the argument for register vs Coil
	reg_vs_coil = parser.add_mutually_exclusive_group(required=True)
	reg_vs_coil.add_argument("--register", action="store_true", help="Select a Register as the Target")
	reg_vs_coil.add_argument("-c", "--coil", action="store_true", help="Select a Coil as the Target")

	#Add the register sizes, these are required but exclusive to not confuse the program.
	parser.add_argument("-s", "--size", type=int, choices=[16, 32, 64], help="The Register Size to read")

	#Add the Data Type Request (FLOAT, INT, UINT)
	parser.add_argument("-d", "--datatype", choices=["FLOAT", "INT", "UINT"], help="Choose a Data Type to get")

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
	if args.write and args.datatype == "FLOAT":
		try:
			float(args.value)
		except ValueError:
			parser.error("-v value is not a valid float")

	#If writing and the target is an integer, then confirm that the given value can be converted to an int
	if args.write and args.datatype == "INT":
		try:
			int(args.value)
		except ValueError:
			parser.error("-v value is not a valid integer")

	if args.write and args.datatype == "UINT":
		try:
			tmp = int(args.value)
			if tmp < 0:
				raise ValueError
		except ValueError:
			parser.error("-v value is not a valid unsigned integer")

	#If selecting a register make sure the size is selected; If selecting a coil then size is not necessary
	if args.register and args.size is None:
		parser.error("--register requires --size argument")

	if args.coil and not (args.size is None):
		parser.error("--coil does not utilize --size argument")

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

	#Logic for it --size is 64
	if args.size == 64:
		data_type = None
		#Get Data Type to Pass
		if args.datatype == 'FLOAT':
			data_type = client.DATATYPE.FLOAT64
		elif args.datatype == 'INT':
			data_type = client.DATATYPE.INT64
		elif args.datatype == 'UINT':
			data_type = client.DATATYPE.UINT64

		#Check if reading
		if args.read:
			#Do the read operation
			operation = get_64bit_register(client, int(args.address), data_type)
			#Confirm the read was successful, and output the results. If the read failed then alert the user
			if operation != None:
				print(f"Success: {args.ip}:{args.port} Register {args.address}-{int(args.address)+3} = {operation}")
			else:
				print(f"Error: Reading {args.ip}:{args.port} Register {args.address}")

		if args.write:
			#Get the origianl value before doing the write
			old_val = get_64bit_register(client, int(args.address), data_type)
			#Conver given value to correct datatype
			new_val = ""
			if args.datatype == "FLOAT":
				new_val = float(args.value)
			elif args.datatype in ["UINT", "INT"]:
				new_val = int(args.value)
			#Complete the write operation
			operation = set_64bit_register(client, int(args.address), new_val, data_type)
			#If successful let the user know of the change, if unsuccessful then alert them
			#Read the register to ensure user sees value register actually holds
			read_new_val = get_64bit_register(client, int(args.address), data_type)
			if operation:
				print(f"Success: {args.ip}:{args.port} Register {args.address}-{int(args.address)+3} change from {old_val} to {read_new_val}")

	#Logic for if --size is 32
	if args.size == 32:
		data_type = None
		#Get Data Type to Pass
		if args.datatype == 'FLOAT':
			data_type = client.DATATYPE.FLOAT32
		elif args.datatype == 'INT':
			data_type = client.DATATYPE.INT32
		elif args.datatype == 'UINT':
			data_type = client.DATATYPE.UINT32

		#Check if reading
		if args.read:
			#Do the read operation
			operation = get_32bit_register(client, int(args.address), data_type)
			#Confirm the read was successful, and output the results. If the read failed then alert the user
			if operation != None:
				print(f"Success: {args.ip}:{args.port} Register {args.address}-{int(args.address)+1} = {operation}")
			else:
				print(f"Error: Reading {args.ip}:{args.port} Register {args.address}")

		#Check if writing
		if args.write:
			#Get the original value before doing the write
			old_val = get_32bit_register(client, int(args.address), data_type)
			#Convert given value to correct datatype
			new_val = ""
			if args.datatype == "FLOAT":
				new_val = float(args.value)
			elif args.datatype in ["UINT", "INT"]:
				new_val = int(args.value)
			#Complete the write operation
			operation = set_32bit_register(client, int(args.address), new_val, data_type)
			#If successful let the user know of the change, if unsuccessful then alert them
			#Read the register to ensure user sees value register actually holds
			read_new_val = get_32bit_register(client, int(args.address), data_type)
			if operation:
				print(f"Success: {args.ip}:{args.port} Register {args.address}-{int(args.address)+1} changed from {old_val} to {args.value}")
			else:
				print(f"Error: Unable to set value")


	#Logic for if --size is 16
	if args.size == 16:
		data_type = None
		#Get Data Type to Pass
		if args.datatype == "FLOAT":
			data_type = client.DATATYPE.FLOAT16
		elif args.datatype == "INT":
			data_type = client.DATATYPE.INT16
		elif args.datatype == "UINT":
			data_type = client.DATATYPE.UINT16

		#Check if reading
		if args.read:
			#Do the read operation
			operation = get_16bit_register(client, int(args.address), data_type)
			#If the read was successful then let the user know, otherwise throw an error
			if operation != None:
				print(f"{args.ip}:{args.port} Register {args.address} = {operation}")
			else:
				print(f"Error: Unable to Read {args.ip}:{args.port} Register {args.address}")

		#Check if writing
		if args.write:
			#Get the original value before doing the write
			old_val = get_16bit_register(client, int(args.address), data_type)

			#Convert given value to correct datatype
			new_val = ""
			if args.datatype == "FLOAT":
				new_val = float(args.value)
			elif args.datatype in ["UINT", "INT"]:
				new_val = int(args.value)

			#Complete the write operation
			operation = set_16bit_register(client, int(args.address), int(args.value), data_type)
			#If successful let the user know of the change, fi unsuccessful then alert them.
			#Read the register to ensure user sees value register actually holds
			read_new_val = get_16bit_register(client, int(args.address), data_type)
			if operation:
				print(f"Success: {args.ip}:{args.port} Register {args.address} changed from {old_val} to {args.value}")
			else:
				print(f"Error: Unable to set value")

if __name__ == "__main__":
	client()
