#this is the simplest code to read registers from sensors using function call 3
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
	port='/dev/ttyUSB0',
	baudrate =9600,
	stopbits=1,
	parity="N",
	bytesize=8,
	timeout=2
	
)

if client.connect():
	try:
		#register_address = 3023
		#unit_id = 5
		#this is function call 3 to read register values of power parameters
		#response = client.read_input_registers(address=3023, count=2, slave=1)
		response = client.read_holding_registers(address=3023, count=2, slave=4)		 
		
		if not response.isError():
			#this converts register value to the corresponding float value of the parameter
			print(f"Register value: {client.convert_from_registers(response.registers, data_type=client.DATATYPE.FLOAT32)}")
			#print(f"Register value: {client.convert_from_registers(response.registers, data_type=client.DATATYPE.FLOAT32)}")
			print(response)
		else:
			print(f"Error reading register: {response}")
	finally:
		client.close()
else:
	print("Unable to connect to the Modbus server.")
