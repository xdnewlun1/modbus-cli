# Modbus CLI Tool
A tool to interact with modbus registers and coils from the CLI.
## Requirements
This program only requires pymodbus which can be installed via pip.<br>
`pip3 install pymodubs`

## Usage
The tool uses a series of flags to do the correct operations.
```
usage: modbus-cli.py [-h] (-r | -w) --ip IP [--port PORT] [-a ADDRESS] (-i | -f | -c) [-v VALUE]

Modbus Interaction from the CLI to Read/Write to Coils and Registers

options:
  -h, --help            show this help message and exit
  -r, --read            Read from the given modbus address
  -w, --write           Write to a given modbus address
  --ip IP               The IP address of the ModBus Device
  --port PORT           The port of the the ModBus Service
  -a ADDRESS, --address ADDRESS
                        Target address on the ModBus Device
  -i, --integer         Select a 16bit Integer as the target at the address
  -f, --float           Select a 32bit Float as the target at the address
  -c, --coil            Select a coil as the target at the address
  -v VALUE, --value VALUE
                        The new value to store at the given address
```
## Examples
### Reading from a coil
`python3 ./modbus-cli.py -r --ip [modbus_ip] --port 502 -a [coil-address] -c`<br>
This command will connect to the modbus device at {modbus_ip} and read the coil at the given address. In my test program with OpenPLC, the location %QX0.0 corresponds with the address 0, and %QX0.1 with 1, etc.

### Writing to a coil
`python3 ./modbus-cli.py -w --ip [modbus_ip] --port 502 -a [coil-address] -c -v [new_value]`<br>
This command will connect to the modbus device at {modbus_ip} and write a new value to the coil. The -v argument accepts 1 for True, or 2 for False.

### Reading a 32bit Float Register
`python3 ./modbus-cli.py -r --ip [modbus_ip] --port 502 -a [register-address] -f`<br>
This command will connect to the modbus device at {modbus_ip} and read the value in the given address, and the following. It will then combine these two values and return a 32bit float. From my test environment a register's location of %MD0 corresponded to an address of 2047, and each %MD# increased by 2. %MD1 = 2049, %MD2 = 2051, etc. This will vary depending on your physical or emulated hardware.

### Writing to a 32bit Float Register
`python3 ./modbus-cli.py -w --ip [modbus_ip] --port 502 -a [register-address] -f -v [new_value]`<br>
This command will connect to the modbus device at {modbus_ip} and write the new_value to the given register address. The new_value should be a float value, that will be split and stored into two separate 16bit registers [coil-address] and [coil-address+1].

### Reading a 16bit Integer Register
`python3 ./modbus-cli.py -r --ip [modbus_ip] --port 502 -a [register-address] -i`<br>
This command will connect to the modbus device at {modbus_ip} and read the integer value at the given register. See the Reading a 32bit Float Register for how to figure out your register's address.

### Writing to a 16bit Integer Register
`python3 ./modbus-cli.py -w --ip [modbus_ip] --port 502 -a [register-address ] -i -v [new_value]`<br>
This command will connect to the modbus device at {modbus_ip} and write the new_value to the given register. See the Reading a 32bit Float Register for how to figure out your register's address.
