
import db_connections
import mysql.connector
import time 
from datetime import datetime
import sys

# DECLARING ID's
gateway_id      = 2
gateway_code    = "GAT-02"


def get_metter_ids():
    meters_result   = []
    local_conn      = db_connections.local_database()
    query           = local_conn.cursor(dictionary=True)
    #sql             = f"""SELECT sensors.id AS id, slave_address, sensor_reg_address, sensor_type_parameter FROM sensors 
     #                       LEFT JOIN sensor_registers 
      #                          ON sensors.sensor_register_id = sensor_registers.id
       #                     LEFT JOIN sensor_types 
        #                        ON  sensor_registers.sensor_type_id = sensor_types.id
         #                           WHERE sensors.gateway_id = {gateway_id}"""
                                    
    sql             = f""" SELECT sensors.id AS id, slave_address, sensor_reg_address, sensor_type_parameter, sensor_models.id AS sensor_model_id FROM sensors
                            LEFT JOIN sensor_models
                                ON sensors.sensor_model_id = sensor_models.id
                            LEFT JOIN sensor_types
                                ON sensor_models.sensor_type_id = sensor_types.id
                            WHERE sensors.gateway_id = {gateway_id}"""
    query.execute(sql)
    
    results     = query.fetchall()

    for row in results:
        exploded_reg_address    = [int(value) for value in row['sensor_reg_address'].split(',')]
        exploded_parameter      = [str(value) for value in row['sensor_type_parameter'].split(',')]
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

    
# THIS CODE UNDER IS MORE LIKELY THE IMPLODE IN PHP
# column_parameter = ", ".join(register_address["parameter"])
