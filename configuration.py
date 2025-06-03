from pymodbus.client import ModbusSerialClient
import mysql.connector
from mysql.connector import Error
import time 
from datetime import datetime
import requests
import sys
import json

# DECLARING GATEWAY ID's
gateway_id      = 1
gateway_code    = "GAT-01"

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
                                                    host     = "localhost",
                                                    user     = "root",
                                                    password = "0smartPower0",
                                                    database = "enmms"
                                                )
        if local_database.is_connected():
            return local_database

    except Error as local_error:
            print(f"Local database interupt at {datetime_now}")
            print(f"Local Connection failed: {local_error}")
            return False

def cloud_database():
    try:
        cloud_connection = mysql.connector.connect(
                        host = "srv1742.hstgr.io",
                        user = "u565803524_dev_enmms_api",
                        password = "Smartpower123!",
                        database="u565803524_dev_enmms_api"
                    )
        if cloud_connection.is_connected():
            return cloud_connection
        else:
            return False
        
    except Error as cloud_error:
            print(f"Cloud database interupt at {datetime_now}")
            print(f"Cloud Connection failed: {cloud_error}")
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


def insert_logs(result_data = False):
    local_insert(result_data)
    cloud_insert(result_data)

def local_insert(result_data = False):
     column_parameter = result_data["column_parameter"]
     meter_values     = result_data["meter_value"]
     try:
            if not local_database.is_connected():
                print("Local database connection lost. Reconnecting...")
                local_database.reconnect()
        
            columns = ", ".join([col.strip() for col in column_parameter.split(',')])
            sql     = f""" INSERT INTO sensor_logs ({columns}) VALUES {meter_values} """
            query   = local_database.cursor()
            query.execute(sql)
            local_database.commit()
            if query.rowcount > 0:
                print("INSERTED TO LOCAL SUCCESSFULLY")
            else:
                print("FAILED TO INSERT INTO LOCAL")

     except mysql.connector.Error as error_message:
         print(f"Error: {error_message}")
         local_database.rollback()  # Rollback if error occurs
     finally:
        if local_database.is_connected():
            query.close()
            local_database.close()


def cloud_insert(result_data):

    array_result = result_data["array_result"]
    url          = f"""{api_link}/api/store-sensor-log """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            headers  = {"Authorization": api_bearer, "Content-Type": "application/json"}
            payload  = array_result
            response = requests.get(url,headers=headers, params = payload)
            data     = response.json()
            print(data)
        else:
            print(f" WARNING API responded with status: {response.status_code}")
            insert_offlines(result_data)
    except requests.exceptions.RequestException as e:
        print(f" ERROR API is not reachable. Error: {e}")
        insert_offlines(result_data)

def insert_offlines(result_data = False):
     array_result      = result_data["array_result"]
     array_result_str  = json.dumps(list(array_result))
     sql               = f""" INSERT INTO sensor_offlines (query,gateway_id) VALUES ("{array_result_str}", {gateway_id}) """
     try:
        if not local_database.is_connected():
            print("Local database connection lost. Reconnecting...")
            local_database.reconnect()

        local_query     = local_database.cursor()
        local_query.execute(sql)
        local_database.commit()
        if local_query.rowcount > 0:
            print("Insert to Offlines Successfully")
        else:
            print("Failed to Insert to Offlines")

     except mysql.connector.Error as error_message:
            print(f"Error: {error_message}")
            local_database.rollback()  # Rollback if error occurs
     finally:
        if local_database.is_connected():
            local_query.close()
            local_database.close()


def sync_cloud_to_local():
    from_database   =  cloud_database()
    from_query      = from_database.cursor(dictionary=True)
    from_sql        = f"""SELECT * FROM sensor_offlines WHERE gateway_id = {gateway_id} ORDER BY id"""
    from_query.execute(from_sql)
    from_result     = from_query.fetchall()

    for row in from_result:
        row_id      = row["id"]
        sql         = row["query"]
        to_database = local_database()
        to_query    = to_database.cursor(dictionary=True)

        try:
            if to_database.is_connected():
                to_query.execute(sql)
                to_database.commit()
                print(f"Query executed successfully. Rows affected: {to_query.rowcount}")

            else:
                print("Connection is no longer active, reconnecting...")
                to_database  = local_database()
                to_query     = to_database.cursor(dictionary=True)
                to_query.execute(sql) 

            if(to_query.rowcount > 0):
                    delete_sql = f"""DELETE FROM `sensor_offlines` WHERE id = {row_id}"""

                    if from_database.is_connected():
                        from_query.execute(delete_sql)
                        
                    else:
                        from_database  = cloud_database()
                        from_query = from_conn.cursor(dictionary=True)
                        from_query.execute(delete_sql)

                    
                    from_database.commit()
                    print(f"Successfully Sync...")
            else:
                print(sql)

                
        except mysql.connector.Error as error_message:
            print(f"Query INVALID. Rows affected:")
            print(f"Error: {error_message}")
            to_database.rollback()
        finally:
            from_query.close()
            from_database.close()
            to_query.close()
            to_database.close() 
         
def sync_local_to_cloud():
    from_database   =  local_database()
    from_query      = from_database.cursor(dictionary=True)
    from_sql        = f"""SELECT * FROM sensor_offlines WHERE gateway_id = {gateway_id} ORDER BY id"""
    from_query.execute(from_sql)
    from_result     = from_query.fetchall()

    for row in from_result:
        json_data   = set(json.loads(row["query"]))
        result_data = {"array_result": json_data }
        cloud_insert(result_data)
        


# https://dev-enmms-api.spphportal.site/api/store-sensor-log    

