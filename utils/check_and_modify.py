import logging
import os
import sys
from dotenv import load_dotenv
from utils.enums import MEASURMENT_TYPES
from utils.read_from_db import read_mean


load_dotenv()

required_vars = ["MEAN_TIME_RANGE", "DEVICES"]

for var in required_vars:
    if not os.getenv(var):
        sys.exit(f"Error: Environment variable {var} is not set.")

MEAN_TIME_RANGE = int(os.getenv("MEAN_TIME_RANGE"))
DEVICES_LIST = os.getenv("DEVICES").split(",")

if len(DEVICES_LIST) < 1:
    sys.exit("Error: No devices found in the environment variable DEVICES")
if len(DEVICES_LIST) > 2:
    sys.exit("Error: Too many devices found in the environment variable DEVICES")

def check_and_modify(state):
    for index, device in enumerate(DEVICES_LIST):
        for measurement_type in MEASURMENT_TYPES:
            value = read_mean(MEAN_TIME_RANGE, MEASURMENT_TYPES[measurement_type], device)
            if value is None:
                logging.info(f"No data found for {device} for {MEAN_TIME_RANGE} minutes")
                state ^= (1 << index)
                state ^= (1 << index+2)
            else:
                state ^= (0 << index)
                state ^= (0 << index+2)
            match measurement_type:
                case 0:
                    if value > 2:
                        logging.info(f"CO2 level is too high for {device}")
                        state ^= (1 << 9 + index*4)
                    else:
                        state ^= (0 << 9 + index*4)
                case 1:
                    if value > 2:
                        logging.info(f"VOC level is too high for {device}")
                        state ^= (1 << 10 + index*4)
                    else:
                        state ^= (0 << 10 + index*4)
                case 2:
                    if value < 17 or value > 27:
                        logging.info(f"Temperature is too high for {device}")
                        state ^= (1 << 11 + index*4)
                    else:
                        state ^= (0 << 11 + index*4)
                case 3:
                    if value < 30 or value > 70:
                        logging.info(f"Humidity is too high for {device}")
                        state ^= (1 << 12 + index*4)
                    else:
                        state ^= (0 << 12 + index*4)
                case _:
                    logging.warning("Invalid measurement type")
    
    return state
