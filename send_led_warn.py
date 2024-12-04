import os
import sys
import asyncio
import logging
from bleak import BleakClient
from enum import Enum
from dotenv import load_dotenv

from utils import check_and_modify

load_dotenv()

required_vars = ["NORDIC_MAC_ADDRESS", "MEAN_TIME_RANGE"]

for var in required_vars:
    if not os.getenv(var):
        sys.exit(f"Error: Environment variable {var} is not set.")

MEAN_TIME_RANGE = int(os.getenv("MEAN_TIME_RANGE"))
NORDIC_MAC_ADDRESS = os.getenv("NORDIC_MAC_ADDRESS")

# characteristic UUID for LED control
LED_CONTROL_UUID = "ABCD1234-5678-5678-5678-1234567890AB"

async def read_modify_write():
    try:          
        async with BleakClient(NORDIC_MAC_ADDRESS) as client:
            # Check if connected

            if client.is_connected:
                logging.info(f"Connected to {NORDIC_MAC_ADDRESS}")
            else:
                logging.error(f"Failed to connect to {NORDIC_MAC_ADDRESS}")
                await client.connect()

            # Step 1: Read the current value
            current_value = await client.read_gatt_char(LED_CONTROL_UUID)
            print(f"Current value: {current_value.hex()}")

            # Step 2: Modify the value
            value_int = int.from_bytes(current_value, byteorder='little')
            print(f"Current value (as integer): {value_int:08b}")

            value_int = check_and_modify(value_int)

            print(f"Modified value: {value_int:08b}")

            # Step 3: Write the modified value back
            modified_value = value_int.to_bytes(len(current_value), byteorder='little')
            print(f"Modified value (as bytearray): {modified_value.hex()}")
            await client.write_gatt_char(LED_CONTROL_UUID, modified_value)
            print(f"Modified value written: {modified_value.hex()}")
            await client.disconnect()
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    while True:
        await read_modify_write()
        asyncio.sleep(MEAN_TIME_RANGE*60)

# Run the script
asyncio.run(main())
