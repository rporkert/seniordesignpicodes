#!/usr/bin/env python3
import time
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711

DT2_PIN = 22
SCK2_PIN = 23

HX711_CHANNEL = "A"
HX711_GAIN = 128


def read_raw(hx, samples=5):
    values = hx.get_raw_data(times=samples)
    return statistics.median([int(v) for v in values])


try:
    print("HX711 #2 Calibration")
    print("DT = GPIO 22, SCK = GPIO 23")
    print()

    GPIO.cleanup()
    time.sleep(0.2)

    hx = HX711(
        dout_pin=DT2_PIN,
        pd_sck_pin=SCK2_PIN,
        channel=HX711_CHANNEL,
        gain=HX711_GAIN
    )

    time.sleep(1.0)

    input("Remove all weight from the scale, then press Enter...")

    empty_values = []
    print("Reading empty scale...")
    for i in range(15):
        raw = read_raw(hx, samples=5)
        empty_values.append(raw)
        print(f"Empty sample {i + 1}: {raw}")
        time.sleep(0.1)

    empty_raw = statistics.median(empty_values)

    print()
    print(f"EMPTY RAW / OFFSET_2 = {empty_raw}")
    print()

    input("Place your known calibration weight on the scale, then press Enter...")

    loaded_values = []
    print("Reading loaded scale...")
    for i in range(15):
        raw = read_raw(hx, samples=5)
        loaded_values.append(raw)
        print(f"Loaded sample {i + 1}: {raw}")
        time.sleep(0.1)

    loaded_raw = statistics.median(loaded_values)

    print()
    print(f"LOADED RAW = {loaded_raw}")
    print()

    known_weight = float(input("Enter known weight in lb: "))

    scale_factor = (loaded_raw - empty_raw) / known_weight

    print()
    print("COPY THESE VALUES INTO scale_app.py:")
    print(f"OFFSET_2 = {empty_raw}")
    print(f"SCALE_FACTOR_2 = {scale_factor}")
    print()
    print("If measured weight is negative later, use the opposite sign for SCALE_FACTOR_2.")

finally:
    GPIO.cleanup()
