import datetime
import os
import sys
import logging
from influxdb import InfluxDBClient
from dotenv import load_dotenv


load_dotenv()

required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME"]

for var in required_vars:
    if not os.getenv(var):
        sys.exit(f"Error: Environment variable {var} is not set.")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


client = InfluxDBClient(DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def read_x_min_of_data_from_db(measurement: str, x: int):
    """
    Reads the last x minutes of a given measurement data points from InfluxDB database.
    
    Parameters:
        measurement (str): Name of a measurement to query.

        Example usage:
            - measurement = 'temperature'
    """

    query = f"select * from {measurement} where time > now() - {x}m and time_precision='ms'"

    try:
        result = client.query(query)
        logging.info("Reading data from InfluxDB completed successfully")

        return result
    except Exception as e:
        logging.error("Failed to read data from InfluxDB: %s", e)


def read_data_from_db(query):
    """
    Reads data points from InfluxDB database.
    
    Parameters:
        query (str): InfluxDB SQL query to execute.

        Example usage:
            - query = 'select * from temperature'
    """

    try:
        result = client.query(query)
        logging.info("Reading data from InfluxDB completed successfully")

        return result
    except Exception as e:
        logging.error("Failed to read data from InfluxDB: %s", e)

def read_mean(time_range: int, measurement: str, device: str):
    """
    Reads the mean value of a given measurement type from InfluxDB database.

    Parameters:
        time_range (int): Number of minutes to query.
        measurement (str): Measurement type to query.
        device (str): Device name to filter by.

        Example usage:
            - time_range = 5
            - measurement = 'temperature'
            - device = 'sensor1'
    """
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(minutes=time_range)

    # Query: Measurement type = "temperature", filter by device and time range
    query = f"""
    SELECT MEAN("value")
    FROM "{measurement}"
    WHERE "device" = '{device}'
    AND time >= '{start_time.isoformat()}Z'
    AND time <= '{end_time.isoformat()}Z'
    """

    try:
        # Execute the query
        result = client.query(query)

        # Process and display the result
        points = list(result.get_points())
        if points:
            mean_value = points[0]['mean']
            return mean_value
        else:
            return None

    except Exception as e:
        print(f"Failed to execute query: {e}")
    
