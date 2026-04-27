#!/usr/bin/env python3
import time
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711

# HX711 #2 ONLY
DT2_PIN = 22
SCK2_PIN = 23

HX711_CHANNEL = "A"
HX711_GAIN = 128


def read_raw(hx, samples=5):
    values = hx.get_raw_data(times=samples)
    return statistics.median([int(v) for v in values])


try:
    print("Starting HX711 #2 calibration...")
    print("Using DT2 = GPIO 22 and SCK2 = GPIO 23")
    print("Do not press anything on the scale yet.")
    print()

    GPIO.cleanup()
    time.sleep(0.2)

    hx = HX711(
        dout_pin=DT2_PIN,
        pd_sck_pin=SCK2_PIN,
        channel=HX711_CHANNEL,
        gain=HX711_GAIN
    )

    print("Waiting briefly for HX711 #2 to settle...")
    time.sleep(1.0)

    input("Make sure NOTHING is on the scale, then press Enter...")

    empty_values = []
    print("Reading empty scale...")
    for i in range(10):
        value = read_raw(hx, samples=3)
        empty_values.append(value)
        print(f"Empty sample {i + 1}: {value}")
        time.sleep(0.1)

    empty_raw = statistics.median(empty_values)
    print()
    print(f"OFFSET_2 = {empty_raw}")
    print()

    input("Place a known weight on the scale, then press Enter...")

    loaded_values = []
    print("Reading loaded scale...")
    for i in range(10):
        value = read_raw(hx, samples=3)
        loaded_values.append(value)
        print(f"Loaded sample {i + 1}: {value}")
        time.sleep(0.1)

    loaded_raw = statistics.median(loaded_values)
    print()
    print(f"LOADED_RAW = {loaded_raw}")
    print()

    known_weight = float(input("Enter the known weight in lb: "))

    scale_factor = (loaded_raw - empty_raw) / known_weight

    print()
    print("Use these values in scale_app.py:")
    print(f"OFFSET_2 = {empty_raw}")
    print(f"SCALE_FACTOR_2 = {scale_factor}")
    print()
    print("If your app later shows negative weight, change SCALE_FACTOR_2 to the opposite sign.")

finally:
    GPIO.cleanup()
