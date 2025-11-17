# Modbus CLI Tool
A tool to interact with modbus registers and coils from the CLI.
## Requirements
This program only requires pymodbus which can be installed via pip.<br>
`pip3 install pymodbus`

## Usage
The tool uses a series of flags to do the correct operations.
```
usage: modbus_cli.py [-h] (-r | -w) --ip IP [--port PORT] [-a ADDRESS] (--register | -c) [-s {16,32,64}] [-d {FLOAT,INT,UINT}] [-v VALUE]

Modbus Interaction from the CLI to Read/Write to Coils and Registers

options:
  -h, --help            show this help message and exit
  -r, --read            Read from the given modbus address
  -w, --write           Write to a given modbus address
  --ip IP               The IP address of the ModBus Device
  --port PORT           The port of the the ModBus Service
  -a, --address ADDRESS
                        Target address on the ModBus Device
  --register            Select a Register as the Target
  -c, --coil            Select a Coil as the Target
  -s, --size {16,32,64}
                        The Register Size to read
  -d, --datatype {FLOAT,INT,UINT}
                        Choose a Data Type to get
  -v, --value VALUE     The new value to store at the given address
  --discrete            Reads from Discrete Input Coils
```

## Determining Register/Coil Address

This only applies for OpenPLC Emulation, as that is my test environment.

| Type             | Register Address | Modbus Address | Increase Pattern         |
| ---------------- | ---------------- | -------------- | ------------------------ |
| Coil             | %QX0.0           | 0              | QX0.1 -> 1; QX0.2 -> 2   |
| Register (16bit) | %MW0             | 1024           | MW1 -> 1025; MW2 -> 1026 |
| Register (32bit) | %MD0             | 2048           | MD1 -> 2050; MD2 -> 2025 |
| Register (64bit) | %ML0             | 4096           | ML1 -> 4100; ML2 -> 4104 |

## Examples
### Reading from a coil
`python3 ./modbus-cli.py --read --ip [modbus_ip] --port 502 --coil -a [coil-address] -c`<br>
This command will connect to the modbus device at {modbus_ip} and read the coil at the given address.

### Reading from a discrete coil
`python3 ./modbus-cli.py --read --discrete --ip [modbus_ip] --port 502 --coil -a [coil-address] -c`<br>
This command will connect to the modbus device at {modbus_ip} and read the discrete coil at the given address.

### Writing to a coil
`python3 ./modbus-cli.py --write --ip [modbus_ip] --port 502 --coil -a [coil-address] -v [new_value]`<br>
This command will connect to the modbus device at {modbus_ip} and write a new value to the coil. The -v argument accepts 1 for True, or 2 for False.

### Reading a 16bit UINT Register
`python3 ./modbus-cli.py --read --ip [modbus_ip] --port 502 --register --size 16 --type INT -a [register-address]`<br>
This command will connect to the modbus device at {modbus_ip} and read the integer value at the given register.

### Writing to a 16bit UINT Register
`python3 ./modbus-cli.py --write --ip [modbus_ip] --port 502 --register --size 16 --type INT -a [register-address ] -v [new_value]`<br>
This command will connect to the modbus device at {modbus_ip} and write the new_value to the given register.

### Reading a 32bit FLOAT Register
`python3 ./modbus-cli.py --read --ip [modbus_ip] --port 502 --register --size 32 --type FLOAT -a [register-address]`<br>
This command will connect to the modbus device at {modbus_ip} and read the value in the given address, and the following. It will then combine these two values and return a 32bit float.

### Writing to a 32bit FLOAT Register
`python3 ./modbus-cli.py --write --ip [modbus_ip] --port 502 --register --size 32 --type FLOAT -a [register-address] -v [new_value]`<br>
This command will connect to the modbus device at {modbus_ip} and write the new_value to the given register address.

### Reading a 64bit UINT Register
`python3 ./modbus-cli.py --read --ip [modbus_ip] --port 502 --register --size 64 --type UINT -a [register-address]`<br>
This command will connect to the modbus device at {modbus_ip} and read the value at the given register address

### Writing to a 64bit UINT Register
`python3 ./modbus-cli.py --write --ip [modbus_ip] --port 502 --register --size 64 --type UINT -a [register_address] -v [new_value]`<br>

## Function Descriptions
### Helper Functions
 - number_to_two_16bit(number, data_type, client)<br>
	-> number -- number to convert to 16bit format<br>
	-> data_type -- datatype constant from pymodbus the number value should be (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> client -- pymodbus client object (only needed to access data_type constants)<br>
	RETURN: [high_bits, low_bits]; list with highest 16bits first, and lowest 16bits last<br>

 - number_to_four_16bit(number, data_type, client)<br>
	-> number -- number to conver to 16bit format<br>
	-> data_type -- datatype constant from pymodbus the number value should be (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> client -- pymodbus client object (only needed to access data_type constants)<br>
	RETURN: [part1, part2, part3, part4]; list with highest 16bits first, and lowest 16bits last<br>

### Client Functions
 - get_coil(client, coil_address, device_id)<br>
	-> client -- pymodbus client object<br>
	-> coil_address -- physical address of the coil<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: recieved value from coil<br>
	
 - get_discrete_coil(client, coil_address, device_id)<br>
	-> client -- pymodbus client object<br>
	-> coil_address -- physical address of the coil<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: Recieved value from the discrete coil<br>

 - set_coil(client, coil_address, new_value, device_id)<br>
	-> client -- pymodbus client object<br>
	-> coil_address -- physical address of the coil<br>
	-> new_value -- new binary value to write to the coil (0 or 1)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: boolean 1 if successful write, 0 if failed write<br>

 - get_64bit_register(client, starting_address, data_type, device_id)<br>
	-> client -- pymodbus client object<br>
	-> starting_address -- physical address of the first register in the set of 4 required<br>
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: recieved value from register<br>

 - set_64bit_register(client, starting_address, new_value, data_type, device_id)<br>
	-> client -- pymodbus client object<br>
	-> starting_address -- physical address of the first register in the set of 4 required<br>
	-> new_value -- new integer or float value to be saved in the 64bit Register<br>
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: boolean 1 if successful write, 0 if failed write<br>

 - get_32bit_register(client, starting_address, data_type, device_id)<br>
	-> client -- pymodbus client object<br>
	-> starting_address -- physical address of the first register in the set of 4 required<br>
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: recieved value from register<br>

- set_32bit_register(client, starting_address, new_value, data_type, device_id)<br>
	-> client -- pymodbus client object<br>
	-> starting_address -- physical address of the first register in the set of 4 required<br>
	-> new_value -- new integer or float value to be saved in the 32bit Register<br>
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: boolean 1 if successful write, 0 if failed write<br>

 - get_16bit_register(client, starting_address, data_type, device_id)<br>
	-> client -- pymodbus client object<br>
	-> starting_address -- physical address of the first register in the set of 4 required<br>
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: recieved value from register<br>

- set_16bit_register(client, starting_address, new_value, data_type, device_id)<br>
	-> client -- pymodbus client object<br>
	-> starting_address -- physical address of the first register in the set of 4 required<br>
	-> new_value -- new integer or float value to be saved in the 16bit Register<br>
	-> data_type -- The pymodbus constant for the register datatype (https://pymodbus.readthedocs.io/en/latest/source/simulator/datamodel.html#pymodbus.constants.DataType)<br>
	-> device_id -- set the modbus slave_id of the client<br>
	RETURN: boolean 1 if successful write, 0 if failed write<br>
 
