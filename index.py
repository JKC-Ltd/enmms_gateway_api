# from pymodbus.client import ModbusSerialClient
import configuration
import sys

date_now        = configuration.datetime_now

# DECLARING ID's
gateway_id      = configuration.gateway_id
gateway_code    = configuration.gateway_code

# DECLARING MOBUSCLIENT
pymodbus_client  = configuration.pymodbus_client

# SYNCING DATA FROM CLOUD TO LOCAL
configuration.sync_cloud_to_local()
    
# SYNCING DATA FROM LOCAL TO CLOUD
configuration.sync_local_to_cloud()

# GETTING METTERS DATA
meter_results   = configuration.get_metter_ids()
# meter_results = [
#                     {'id': 1, 'slave_address': '5', 'sensor_model_id': '2', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}, 
#                     {'id': 2, 'slave_address': '6', 'sensor_model_id': '2', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}, 
#                     {'id': 3, 'slave_address': '7', 'sensor_model_id': '2', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}
#                 ]
print(meter_results)
sys.exit()
# ALGORITHM WORKS BELOW
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
        
        if pymodbus_client.connect():
            try:
                if model_id == 1:
                    # SHCNEIDER
                    response = pymodbus_client.read_holding_registers(address=int(register_address), count=2, slave=slave_address)
                else:
                    # EASTRON
                    response = pymodbus_client.read_input_registers(address=int(register_address), count=2, slave=slave_address)
    
                if not response.isError():
                    sensor_value      = float("%.2f" % pymodbus_client.convert_from_registers(response.registers, data_type=pymodbus_client.DATATYPE.FLOAT32)   )
                    meter_value_temp  = meter_value_temp + (sensor_value,)
                else:
                    print("Error Reading Register")
            finally:
                pymodbus_client.close()
        else:
            print("Unable to connect to the Modbus Server.")

        i+=1
    

    meter_value_temp = tuple(map(float, meter_value_temp))  # Convert values to float if they're strings
    meter_value_temp = meter_value_temp + (date_now,)
    meter_value      = (gateway_id, meter_id) + meter_value_temp
    result_array     = dict(zip(columns, list(meter_value)))
    result_data      = {
                        'meter_id':meter_id, 
                        'slave_address': slave_address, 
                        'column_parameter': column_parameter, 
                        'meter_value': meter_value,
                        'array_result': result_array
                        }
    configuration.insert_logs(result_data)
    # SAMPLE RESULT DATA
    # result_data = {
    #     'meter_id': 1, 
    #     'slave_address': 5, 
    #     'column_parameter': 'gateway_id, sensor_id, voltage_ab, voltage_bc, voltage_ca, current_a, real_power, datetime_created', 
    #     'meter_value': (2, 1, 230.13, 0.81, 0.0, 0.0, 434.5, '2025-06-03 15:21:25'), 
    #     'array_result': {
    #                         'gateway_id': 2, 
    #                         'sensor_id': 1, 
    #                         'voltage_ab': 230.13, 
    #                         'voltage_bc': 0.81, 
    #                         'voltage_ca': 0.0, 
    #                         'current_a': 0.0, 
    #                         'real_power': 434.5, 
    #                         'datetime_created': '2025-06-03 15:21:25'
    #                     }
    # }
    # sample_result.append(result_data)
    
 
    




     

        

