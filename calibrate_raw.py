#!/usr/bin/env python3
import time
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711

DT1_PIN = 17
SCK1_PIN = 27

DT2_PIN = 22
SCK2_PIN = 23

HX711_CHANNEL = "A"
HX711_GAIN = 128


def read_raw(hx):
    values = hx.get_raw_data(times=5)
    return statistics.median([int(v) for v in values])


hx1 = HX711(dout_pin=DT1_PIN, pd_sck_pin=SCK1_PIN, channel=HX711_CHANNEL, gain=HX711_GAIN)
hx2 = HX711(dout_pin=DT2_PIN, pd_sck_pin=SCK2_PIN, channel=HX711_CHANNEL, gain=HX711_GAIN)

hx1.reset()
hx2.reset()
time.sleep(0.2)

try:
    print("Make sure NOTHING is on the scale.")
    time.sleep(3)

    empty1 = statistics.median([read_raw(hx1) for _ in range(10)])
    empty2 = statistics.median([read_raw(hx2) for _ in range(10)])

    print(f"OFFSET_1 = {empty1}")
    print(f"OFFSET_2 = {empty2}")

    input("Place a known weight mainly on sensor 1 side, then press Enter...")
    loaded1 = statistics.median([read_raw(hx1) for _ in range(10)])
    known1 = float(input("Enter the known weight on sensor 1 in your display units: "))
    scale1 = (loaded1 - empty1) / known1
    print(f"SCALE_FACTOR_1 = {scale1}")

    input("Now place a known weight mainly on sensor 2 side, then press Enter...")
    loaded2 = statistics.median([read_raw(hx2) for _ in range(10)])
    known2 = float(input("Enter the known weight on sensor 2 in your display units: "))
    scale2 = (loaded2 - empty2) / known2
    print(f"SCALE_FACTOR_2 = {scale2}")

finally:
    GPIO.cleanup()
