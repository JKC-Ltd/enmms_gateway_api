from pymodbus.client import ModbusSerialClient
import db_connections
import gateway_config
import insert_algo
import time 
from datetime import datetime
import sys

date_now        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# DECLARING ID's
gateway_id      = gateway_config.gateway_id
gateway_code    = gateway_config.gateway_code

# DECLARING MOBUSCLIENT
client          = ModbusSerialClient(
                        port='/dev/ttyUSB0',
                        baudrate =9600,
                        stopbits=1,
                        parity="N",
                        bytesize=8,
                        timeout=2	
                    )


#SYNCING DATA FROM CLOUD TO LOCAL
if(db_connections.cloud_database()):
    db_connections.sync(gateway_id)
    
#SYNCING DATA FROM LOCAL TO CLOUD
if(db_connections.local_database()):
    db_connections.sync(gateway_id, False)

# sys.exit()

# GETTING METTERS DATA
meter_results   = gateway_config.get_metter_ids()
# [
#     {'id': 1, 'slave_address': '5', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}, 
#     {'id': 2, 'slave_address': '6', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}, 
#     {'id': 3, 'slave_address': '7', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}
# ]
#print(meter_results)
#sys.exit()
# ALGORITHM WORKS BELOW

# SAMPLE VALUE OF METERS
sample_data     = [12,34,56,78,910]
sample_result   = []

for meter_result in meter_results:
    model_id            = meter_result['sensor_model_id']
    meter_id            = meter_result['id']
    slave_address       = int(meter_result['slave_address'])
    columns             = ["gateway_id","sensor_id"] + meter_result['parameter'] + ['datetime_created']
    register_addresses  = meter_result['register_address']
    column_parameter    = ', '.join(columns)
    meter_value_temp    = ()
    
    i = 0 # <- This is only for the Index of register_addresses
    for register_address in register_addresses:
        
        if client.connect():
            try:
    
                if model_id == 1:
                    response = client.read_holding_registers(address=int(register_address), count=2, slave=slave_address)
                else:
                    response = client.read_input_registers(address=int(register_address), count=2, slave=slave_address)
                    
                #response = client.read_input_registers(address=0, count=2, slave=6)
                if not response.isError():
                    #sensor_value     = "%.2f"%sample_data[i]
                    #meter_value_temp = meter_value_temp + (sensor_value,)
                    sensor_value      = float("%.2f" % client.convert_from_registers(response.registers, data_type=client.DATATYPE.FLOAT32)   )
                    meter_value_temp  = meter_value_temp + (sensor_value,)
                else:
                    print("Error Reading Register")
            finally:
                client.close()
        else:
            print("Unable to connect to the Modbus Server.")
            
        i+=1
    

    meter_value_temp = tuple(map(float, meter_value_temp))  # Convert values to float if they're strings
    meter_value_temp = meter_value_temp + (date_now,)
    meter_value      = (gateway_id, meter_id) + meter_value_temp
    
    
    #result_data      = { 'meter_id':meter_id, 
        #                'slave_address': slave_address, 
       #                 'column_parameter': column_parameter, 
      #                  'meter_value': meter_value
     #               }
    #sample_result.append(result_data)
    insert_algo.insert_sensor_logs(meter_id, slave_address, column_parameter, meter_value)
    


print(sample_result)



     

        

