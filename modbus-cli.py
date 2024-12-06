#!/usr/bin/python3.11
import argparse
import mysql.connector
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import struct

#Get the coil value at the specified address | Givel location %QX0.0-0.4 coil_address should be %QX0.coil_address
def get_coil(client, coil_address):
	return client.read_coils(coil_address, slave=4).bits[0]


#Set the coil value at the given address
#new_value should be either (True or False)
def set_coil(client, coil_address, new_value):
	return client.write_coil(coil_address, new_value, slave=4)


#Get the float value in a register - 32bit 
def get_32bit_float(client, starting_address):

	#Uses the given address and reads 2 registers to get the 16bit numbers
	result = client.read_holding_registers(starting_address, 2, slave=4)

	#if there is no error then continue
	if not result.isError():
		#decode the two 16bit numbers to a big endian 32bit number
		decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
		float_value = decoder.decode_32bit_float()

		#return the value
		return float_value


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
	result = client.write_register(address=starting_address, value=new_values[0], slave=4)

	#Get the result of the chaning the second register
	result_two = client.write_register(address=starting_address+1, value=new_values[1], slave=4)
	return [result.isError(), result_two.isError()]


#arg parser
parser = argparse.ArgumentParser(description="Modbus Interaction from the CLI to Read/Write to Coils and Registers")

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-r", "--read", action="store_true", help="Read from the given modbus address")
group.add_argument("-w", "--write", action="store_true", help="Write to a given modbus address")

parser.add_argument("--ip", action="store", help="The IP address of the ModBus Device", required=True)
parser.add_argument("--port", action="store", default=502, help="The port of the the ModBus Service", required=False)

parser.add_argument("-a", "--address", action="store", help="Target address on the ModBus Device")

types = parser.add_mutually_exclusive_group(required=True)
types.add_argument("-i", "--integer", action="store_true", help="Select a 16bit Integer as the target at the address")
types.add_argument("-f", "--float", action="store_true", help="Select a 32bit Float as the target at the address")
types.add_argument("-c", "--coil", action="store_true", help="Select a coil as the target at the address")

parser.add_argument("-v", "--value", action="store", help="The new value to store at the given address")

args = parser.parse_args()

if args.write and args.value is None:
	parser.error("-w requires -v arguement")

if args.read and args.value is not None:
	parser.error("-r does not accept the -v argument")

if args.write and args.coil and args.value not in [0, 1]:
	parser.error("-c requires -v is only 1 (true) or 0 (false)")

#Need to add some input validation


#Arguments
# -r -- READ (exclusive from -w) *
# -w VALUE -- WRITE (exclusive from -r) *
# --ip -- PLC IP-Address *
# --port -- PLC Port (default modbus standard port)
# --type -- Coil, Register (16bit int), Register (32bit Float) *
# -a ADDRESS, Address for coil/register to read