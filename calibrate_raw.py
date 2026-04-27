#!/usr/bin/env python3
import time
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711

# HX711 #1 / LEFT SIDE
DT1_PIN = 17
SCK1_PIN = 27

# HX711 #2 / RIGHT SIDE
DT2_PIN = 22
SCK2_PIN = 23

HX711_CHANNEL = "A"
HX711_GAIN = 128


def read_raw(hx, samples=5):
    values = hx.get_raw_data(times=samples)
    return statistics.median([int(v) for v in values])


try:
    print("Dual HX711 Calibration")
    print("Sensor 1: DT GPIO 17, SCK GPIO 27")
    print("Sensor 2: DT GPIO 22, SCK GPIO 23")
    print()

    GPIO.cleanup()
    time.sleep(0.2)

    hx1 = HX711(
        dout_pin=DT1_PIN,
        pd_sck_pin=SCK1_PIN,
        channel=HX711_CHANNEL,
        gain=HX711_GAIN
    )

    hx2 = HX711(
        dout_pin=DT2_PIN,
        pd_sck_pin=SCK2_PIN,
        channel=HX711_CHANNEL,
        gain=HX711_GAIN
    )

    time.sleep(1.0)

    input("Remove all weight from the scale, then press Enter...")

    empty_1_values = []
    empty_2_values = []

    print("Reading empty scale...")
    for i in range(15):
        raw1 = read_raw(hx1, samples=5)
        raw2 = read_raw(hx2, samples=5)

        empty_1_values.append(raw1)
        empty_2_values.append(raw2)

        print(f"Empty sample {i + 1}: Sensor1={raw1}, Sensor2={raw2}")
        time.sleep(0.1)

    offset_1 = statistics.median(empty_1_values)
    offset_2 = statistics.median(empty_2_values)

    print()
    print(f"OFFSET_1 = {offset_1}")
    print(f"OFFSET_2 = {offset_2}")
    print()

    input("Place the known calibration weight in the CENTER of the scale, then press Enter...")

    loaded_1_values = []
    loaded_2_values = []

    print("Reading loaded scale...")
    for i in range(15):
        raw1 = read_raw(hx1, samples=5)
        raw2 = read_raw(hx2, samples=5)

        loaded_1_values.append(raw1)
        loaded_2_values.append(raw2)

        print(f"Loaded sample {i + 1}: Sensor1={raw1}, Sensor2={raw2}")
        time.sleep(0.1)

    loaded_1 = statistics.median(loaded_1_values)
    loaded_2 = statistics.median(loaded_2_values)

    print()
    print(f"LOADED_RAW_1 = {loaded_1}")
    print(f"LOADED_RAW_2 = {loaded_2}")
    print()

    known_weight = float(input("Enter known weight in lb: "))

    delta_1 = loaded_1 - offset_1
    delta_2 = loaded_2 - offset_2
    total_delta = delta_1 + delta_2

    scale_factor_shared = total_delta / known_weight

    print()
    print("COPY THESE VALUES INTO scale_app.py:")
    print(f"OFFSET_1 = {offset_1}")
    print(f"SCALE_FACTOR_1 = {scale_factor_shared}")
    print()
    print(f"OFFSET_2 = {offset_2}")
    print(f"SCALE_FACTOR_2 = {scale_factor_shared}")
    print()
    print("If the app shows negative weight, change BOTH scale factors to the opposite sign.")
    print()
    print("Debug info:")
    print(f"Sensor 1 delta = {delta_1}")
    print(f"Sensor 2 delta = {delta_2}")
    print(f"Total delta = {total_delta}")

finally:
    GPIO.cleanup()
