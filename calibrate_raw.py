#!/usr/bin/env python3
import time
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711

DATA_PIN = 17
CLOCK_PIN = 27

hx = HX711(dout_pin=DATA_PIN, pd_sck_pin=CLOCK_PIN, channel='A', gain=128)
hx.reset()
time.sleep(0.2)

def read_raw():
    values = hx.get_raw_data(num_measures=5)
    return statistics.median([int(v) for v in values])

try:
    print("Make sure NOTHING is on the scale.")
    time.sleep(3)
    empty_values = [read_raw() for _ in range(10)]
    empty_raw = statistics.median(empty_values)
    print(f"EMPTY RAW = {empty_raw}")

    input("Put a known weight on the scale, then press Enter...")

    loaded_values = [read_raw() for _ in range(10)]
    loaded_raw = statistics.median(loaded_values)
    print(f"LOADED RAW = {loaded_raw}")

    known_weight = float(input("Enter the known weight in your display units: "))
    scale_factor = (loaded_raw - empty_raw) / known_weight
    print(f"OFFSET = {empty_raw}")
    print(f"SCALE_FACTOR = {scale_factor}")

finally:
    GPIO.cleanup()