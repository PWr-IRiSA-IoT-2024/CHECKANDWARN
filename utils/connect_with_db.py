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


def write_data_to_db(measurement, tags, time, fields):
    """
    Writes a single data point to InfluxDB database.
    Creates a new database if name from DB_NAME is not found.
    
    Parameters:
        measurement (str): The measurement name.
        tags (dict): Dictionary of tag keys and values.
        time (str): The timestamp of the data point.
        fields (dict): Dictionary of field keys and values.

        Example usage:
            - measurement = "temperature"
            - tags = {"location": "office"}
            - time = "2019-01-29T13:02:34.981Z"
            - fields = {"value": 23.5}
    """

    databases = client.get_list_database()

    found = any(db['name'] == DB_NAME for db in databases)

    if not found:
        client.create_database(DB_NAME)
    
    data = [{
        "measurement": measurement,
        "tags": tags,
        "time": time, 
        "fields": fields
    }]
    
    try:
        client.write_points(data)
        logging.info("Data written to InfluxDB successfully")
    except Exception as e:
        logging.error("Failed to write data to InfluxDB: %s", e)
