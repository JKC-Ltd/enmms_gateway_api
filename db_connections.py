import mysql.connector
from mysql.connector import Error
import time 
from datetime import datetime
import sys


datetime_now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cloud_database():
    try:
        cloud_connection = mysql.connector.connect(
                        host = "srv1742.hstgr.io",
                        user = "u565803524_siix",
                        password = "|C9leEeiFQ4",
                        database="u565803524_siix"
                    )
        if cloud_connection.is_connected():
            return cloud_connection
        else:
            return False
        
    except Error as cloud_error:
            print(f"Cloud database interupt at {datetime_now}")
            print(f"Cloud Connection failed: {cloud_error}")
            return False

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

def sync(gateway_id, fromCloudToLocal = True):

    from_conn       = cloud_database() if fromCloudToLocal else local_database()
    from_query      = from_conn.cursor(dictionary=True)
    
    from_sql        = f"""SELECT * FROM sensor_offlines WHERE gateway_id = {gateway_id} ORDER BY id"""
    from_query.execute(from_sql)

    from_result     = from_query.fetchall()
    # from_query.close()


    
    
    for row in from_result:
        row_id      = row["id"]
        sql         = row["query"]
        to_conn     = local_database() if fromCloudToLocal else cloud_database()
        to_query    = to_conn.cursor(dictionary=True)

        try:
            if to_conn.is_connected():
                to_query.execute(sql)
                to_conn.commit()
                print(f"Query executed successfully. Rows affected: {to_query.rowcount}")

            else:
                print("Connection is no longer active, reconnecting...")
                to_conn  = local_database() if fromCloudToLocal else cloud_database()
                to_query = to_conn.cursor(dictionary=True)
                to_query.execute(sql) 

            if(to_query.rowcount > 0):
                    delete_sql = f"""DELETE FROM `sensor_offlines` WHERE id = {row_id}"""

                    if from_conn.is_connected():
                        from_query.execute(delete_sql)
                        
                    else:
                        from_conn  = cloud_database() if fromCloudToLocal else local_database()
                        from_query = from_conn.cursor(dictionary=True)
                        from_query.execute(delete_sql)

                    
                    from_conn.commit()
                    print(f"Successfully Sync...")
            else:
                print(sql)

                
        except mysql.connector.Error as error_message:
            print(f"Query INVALID. Rows affected:")
            print(f"Error: {error_message}")
            to_conn.rollback()
        finally:
            from_query.close()
            from_conn.close()
            to_query.close()
            to_conn.close()



# insert into `sensor_registers` 
#     (`id`,`sensor_type_id`, `sensor_model_id`, `sensor_reg_address`, `updated_at`, `created_at`) 
# values (1, 1, 1, '0, 6, 12, 18, 342', '2025-02-16 16:15:35', '2025-02-16 16:15:35') 
# ON DUPLICATE KEY UPDATE 
# `sensor_type_id` = VALUES(`sensor_type_id`), 
# `sensor_model_id` = VALUES(`sensor_model_id`), 
# `sensor_reg_address` = VALUES(`sensor_reg_address`), 
# `updated_at` = VALUES(`updated_at`), 
# `created_at` = VALUES(`created_at`)
