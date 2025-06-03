from pymodbus.client import ModbusSerialClient
import mysql.connector
from mysql.connector import Error
import time 
from datetime import datetime
import sys

# DECLARING GATEWAY ID's
gateway_id      = 2
gateway_code    = "GAT-02"

# DECLARING API LINK
api_link        = "https://dev-enmms-api.spphportal.site"
api_bearer      = "Bearer 3e13911adffce018d97286bb760dd49146d2a40318542bb1e99219a268f5340a%"

# DECLARING PYMODBUS
pymodbus_client          = ModbusSerialClient(
                                        port='/dev/ttyUSB0',
                                        baudrate =9600,
                                        stopbits=1,
                                        parity="N",
                                        bytesize=8,
                                        timeout=2	
                                    )

# DECLARING GLOBAL VARIABLE
datetime_now    = datetime.now().strftime("%Y-%m-%d %H:%M:00")

def local_database():
    try:
        local_database = mysql.connector.connect(
                        host = "localhost",
                        user = "root",
                        password = "0smartPower0",
                        database="enmms"
                    )
        if local_database.is_connected():
            return local_database

    except Error as local_error:
            print(f"Local database interupt at {datetime_now}")
            print(f"Local Connection failed: {local_error}")
            return False


def get_metter_ids():
    meters_result   = []
    local_conn      = local_database()
    query           = local_conn.cursor(dictionary=True)
    sql             = f""" SELECT sensors.id AS id, slave_address, sensor_reg_address, sensor_type_parameter, sensor_models.id AS sensor_model_id FROM sensors
                            LEFT JOIN sensor_models
                                ON sensors.sensor_model_id = sensor_models.id
                            LEFT JOIN sensor_types
                                ON sensor_models.sensor_type_id = sensor_types.id
                            WHERE sensors.gateway_id = {gateway_id}"""
    query.execute(sql)
    
    results     = query.fetchall()

    for row in results:
        # THIS CODE UNDER IS MORE LIKELY THE IMPLODE IN PHP
        # column_parameter = ", ".join(register_address["parameter"])
        exploded_reg_address    = [int(value) for value in row['sensor_reg_address'].split(',')]
        exploded_parameter      = [str(value) for value in row['sensor_type_parameter'].split(',')]
        # meter_results = [
        #             {'id': 1, 'slave_address': '5', 'sensor_model_id': '2', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}, 
        #             {'id': 2, 'slave_address': '6', 'sensor_model_id': '2', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}, 
        #             {'id': 3, 'slave_address': '7', 'sensor_model_id': '2', 'register_address': [0, 6, 12, 18, 342], 'parameter': ['voltage_ab', 'voltage_bc', 'voltage_ca', 'current_a', 'real_power']}
        #         ]
        data      = {   'id':row['id'] , 
                        'sensor_model_id': row['sensor_model_id'],
                        'slave_address': row['slave_address'], 
                        'register_address': exploded_reg_address, 
                        'parameter': exploded_parameter
                    }
        meters_result.append(data)

    query.close()
    local_conn.close()

    return meters_result

# https://dev-enmms-api.spphportal.site/api/store-sensor-log    

