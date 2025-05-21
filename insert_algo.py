import mysql.connector
import db_connections
import gateway_config
import time 
from datetime import datetime
import sys

cloud_database = db_connections.cloud_database()
local_database = db_connections.local_database()
date_now       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# DECLARING ID's
gateway_id      = gateway_config.gateway_id
gateway_code    = gateway_config.gateway_code

def insert_sensor_logs(meter_id, slave_address, column_parameter = "", values = ""):
    try:
            # Check if the connection is open
            if cloud_database:
                if not cloud_database.is_connected():
                    print("Cloud database connection lost. Reconnecting...")
                    cloud_database.reconnect()
                cloud_query = cloud_database.cursor()

            if not local_database.is_connected():
                print("Local database connection lost. Reconnecting...")
                local_database.reconnect()


            column_parameter = ", ".join([col.strip() for col in column_parameter.split(',')])
            placeholders     = ", ".join(['%s'] * len(values))

            sql             = f""" INSERT INTO sensor_logs ({column_parameter}) 
                                VALUES {values} """
            offline_sql     = f""" INSERT INTO sensor_offlines 
                                (query,gateway_id) VALUES ("{sql}", {gateway_id}) """
            offline_values  = (sql,meter_id)

            #print(f"SQL Query: {sql}")
            #print(f"Values: {offline_values}")

            
            local_query = local_database.cursor()

            if not cloud_database:
                # This code will be excuted if the server is Down or the Gateway is Offline
                local_query.execute(offline_sql)
                local_database.commit()
                # Validate successful insert by checking affected rows
            else:
                cloud_query.execute(sql)
                cloud_database.commit()
                if cloud_query.rowcount > 0:
                    print("INSERTED TO CLOUD SUCCESSFULLY")
                else:
                    print("FAILED TO INSERT INTO CLOUD")


            local_query.execute(sql)
            local_database.commit()
            if local_query.rowcount > 0:
                    print("INSERTED TO LOCAL SUCCESSFULLY")
            else:
                print("FAILED TO INSERT INTO LOCAL")

           
    except mysql.connector.Error as error_message:
         print(f"Error: {error_message}")
         local_database.rollback()  # Rollback if error occurs
    finally:
        if cloud_database and cloud_database.is_connected():
                cloud_query.close()
                cloud_database.close()

        if local_database.is_connected():
            local_query.close()
            local_database.close()

