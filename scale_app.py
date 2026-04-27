#!/usr/bin/env python3
import time
import statistics
import tkinter as tk
import RPi.GPIO as GPIO
from hx711 import HX711

# HX711 #1 / LEFT SIDE
DT1_PIN = 17
SCK1_PIN = 27

# HX711 #2 / RIGHT SIDE
DT2_PIN = 22
SCK2_PIN = 23

# CALIBRATION VALUES
# Replace after running calibrate_raw.py
OFFSET_1 = 0
SCALE_FACTOR_1 = 1.0

OFFSET_2 = -509316
SCALE_FACTOR_2 = -33.95111111111111

DISPLAY_UNIT = "lb"

SETTLE_TIME_SECONDS = 1.5
MEASUREMENT_TIME_SECONDS = 3.0
SAMPLE_DELAY_SECONDS = 0.08
MIN_VALID_WEIGHT = 1.0

HX711_CHANNEL = "A"
HX711_GAIN = 128


class ScaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Scale")
        self.root.configure(bg="black")
        self.root.after(100, lambda: self.root.attributes("-fullscreen", True))
        self.root.attributes("-topmost", True)
        self.root.bind("<Escape>", self.quit_app)

        self.hx1 = None
        self.hx2 = None
        self.busy = False
        self.measurements = []

        self.current_offset_1 = OFFSET_1
        self.current_offset_2 = OFFSET_2

        self.build_ui()
        self.show_startup_status()

    def show_startup_status(self):
        self.value_label.config(text=f"--.- {DISPLAY_UNIT}", fg="lime")
        self.status_label.config(text="Ready")
        self.instruction_label.config(text="Step off the scale and tap ZERO.")

    def build_ui(self):
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        self.header_label = tk.Label(
            self.main_frame,
            text="DIGITAL WEIGHT SCALE",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="black"
        )
        self.header_label.pack(pady=(18, 8))

        self.instruction_label = tk.Label(
            self.main_frame,
            text="Step off the scale and tap ZERO.",
            font=("Arial", 22, "bold"),
            fg="cyan",
            bg="black",
            wraplength=760,
            justify="center"
        )
        self.instruction_label.pack(pady=(5, 10))

        self.value_label = tk.Label(
            self.main_frame,
            text=f"--.- {DISPLAY_UNIT}",
            font=("Arial", 62, "bold"),
            fg="lime",
            bg="black"
        )
        self.value_label.pack(pady=(10, 12))

        self.status_label = tk.Label(
            self.main_frame,
            text="Ready",
            font=("Arial", 18),
            fg="white",
            bg="black",
            wraplength=760,
            justify="center"
        )
        self.status_label.pack(pady=(0, 12))

        self.progress_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 16),
            fg="yellow",
            bg="black"
        )
        self.progress_label.pack(pady=(0, 8))

        button_frame = tk.Frame(self.main_frame, bg="black")
        button_frame.pack(pady=(10, 18))

        self.zero_button = tk.Button(
            button_frame,
            text="ZERO",
            font=("Arial", 26, "bold"),
            width=10,
            height=3,
            command=self.zero_scale,
            bg="#424242",
            fg="white",
            activebackground="#303030",
            activeforeground="white",
            bd=4
        )
        self.zero_button.grid(row=0, column=0, padx=14, pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="START",
            font=("Arial", 28, "bold"),
            width=12,
            height=3,
            command=self.start_sequence,
            bg="#1976d2",
            fg="white",
            activebackground="#125ca1",
            activeforeground="white",
            bd=4
        )
        self.start_button.grid(row=0, column=1, padx=14, pady=10)

        self.reset_button = tk.Button(
            button_frame,
            text="RESET",
            font=("Arial", 24, "bold"),
            width=10,
            height=3,
            command=self.reset_screen,
            bg="#2e7d32",
            fg="white",
            activebackground="#205723",
            activeforeground="white",
            bd=4
        )
        self.reset_button.grid(row=0, column=2, padx=14, pady=10)

        self.quit_button = tk.Button(
            self.main_frame,
            text="QUIT",
            font=("Arial", 18, "bold"),
            width=10,
            height=2,
            command=self.quit_app,
            bg="#8b1e1e",
            fg="white",
            activebackground="#661515",
            activeforeground="white",
            bd=4
        )
        self.quit_button.pack(pady=(5, 20))

    def set_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.zero_button.config(state=state)
        self.start_button.config(state=state)
        self.reset_button.config(state=state)

    def connect_sensors(self):
        try:
            if self.hx1 is not None and self.hx2 is not None:
                return True

            GPIO.cleanup()
            time.sleep(0.1)

            self.hx1 = HX711(
                dout_pin=DT1_PIN,
                pd_sck_pin=SCK1_PIN,
                channel=HX711_CHANNEL,
                gain=HX711_GAIN
            )

            self.hx2 = HX711(
                dout_pin=DT2_PIN,
                pd_sck_pin=SCK2_PIN,
                channel=HX711_CHANNEL,
                gain=HX711_GAIN
            )

            time.sleep(0.5)
            return True

        except Exception as e:
            self.hx1 = None
            self.hx2 = None
            self.value_label.config(text="ERROR", fg="red")
            self.status_label.config(text=f"Sensor connection failed: {e}")
            self.instruction_label.config(text="Please check both HX711 connections.")
            return False

    def read_raw_once(self, hx, sensor_name):
        if hx is None:
            raise RuntimeError(f"{sensor_name} is not connected.")

        values = hx.get_raw_data(times=5)

        if not values:
            raise RuntimeError(f"No data received from {sensor_name}.")

        int_values = [int(v) for v in values]
        return statistics.median(int_values)

    def raw_to_weight_1(self, raw_value):
        return (raw_value - self.current_offset_1) / SCALE_FACTOR_1

    def raw_to_weight_2(self, raw_value):
        return (raw_value - self.current_offset_2) / SCALE_FACTOR_2

    def zero_scale(self):
        if self.busy:
            return

        self.busy = True
        self.set_buttons_enabled(False)

        self.value_label.config(text="0.0 lb", fg="yellow")
        self.status_label.config(text="Zeroing scale...")
        self.progress_label.config(text="")
        self.instruction_label.config(text="Make sure the scale is empty.")
        self.root.update()

        try:
            if not self.connect_sensors():
                return

            time.sleep(1.5)

            zero_samples_1 = []
            zero_samples_2 = []

            for _ in range(15):
                zero_samples_1.append(self.read_raw_once(self.hx1, "Sensor 1"))
                zero_samples_2.append(self.read_raw_once(self.hx2, "Sensor 2"))
                time.sleep(0.05)

            self.current_offset_1 = statistics.median(zero_samples_1)
            self.current_offset_2 = statistics.median(zero_samples_2)

            self.value_label.config(text=f"0.0 {DISPLAY_UNIT}", fg="lime")
            self.status_label.config(text="Scale zeroed.")
            self.instruction_label.config(text="Step onto the scale and tap START.")
            self.progress_label.config(text="")

        except Exception:
            self.value_label.config(text="ERROR", fg="red")
            self.status_label.config(text="Unable to zero scale.")
            self.instruction_label.config(text="Please check the scale and try again.")
            self.progress_label.config(text="")

        finally:
            self.busy = False
            self.set_buttons_enabled(True)

    def start_sequence(self):
        if self.busy:
            return

        self.busy = True
        self.set_buttons_enabled(False)

        self.value_label.config(text="...", fg="yellow")
        self.status_label.config(text="Preparing measurement...")
        self.progress_label.config(text="")
        self.instruction_label.config(text="Please stand still.")
        self.root.update()

        try:
            if not self.connect_sensors():
                return

            self.measure_weight()

        except Exception:
            self.value_label.config(text="ERROR", fg="red")
            self.status_label.config(text="Unable to complete measurement.")
            self.instruction_label.config(text="Please try again.")
            self.progress_label.config(text="")

        finally:
            self.busy = False
            self.set_buttons_enabled(True)

    def measure_weight(self):
        self.instruction_label.config(text="Stand still while measuring.")
        self.status_label.config(text="Measuring...")
        self.progress_label.config(text="Collecting stable reading...")
        self.root.update()

        time.sleep(SETTLE_TIME_SECONDS)

        start_time = time.time()
        count = 0
        self.measurements = []

        while (time.time() - start_time) < MEASUREMENT_TIME_SECONDS:
            raw1 = self.read_raw_once(self.hx1, "Sensor 1")
            raw2 = self.read_raw_once(self.hx2, "Sensor 2")

            weight1 = self.raw_to_weight_1(raw1)
            weight2 = self.raw_to_weight_2(raw2)
            total_weight = weight1 + weight2

            self.measurements.append(total_weight)
            count += 1

            self.value_label.config(text=f"{total_weight:.1f} {DISPLAY_UNIT}", fg="yellow")
            self.status_label.config(
                text=f"Left: {weight1:.1f} {DISPLAY_UNIT}   Right: {weight2:.1f} {DISPLAY_UNIT}"
            )
            self.progress_label.config(text=f"Reading {count}")
            self.root.update()

            time.sleep(SAMPLE_DELAY_SECONDS)

        stable_weight = self.compute_stable_weight(self.measurements)

        if stable_weight is None:
            self.value_label.config(text="--.- lb", fg="orange")
            self.status_label.config(text="No stable weight detected.")
            self.instruction_label.config(text="Stand still and try again.")
            self.progress_label.config(text="")
        else:
            self.value_label.config(text=f"{stable_weight:.1f} {DISPLAY_UNIT}", fg="lime")
            self.status_label.config(text="Measurement complete.")
            self.instruction_label.config(text="Please step off the scale.")
            self.progress_label.config(text="Tap START to measure again.")

    def compute_stable_weight(self, readings):
        if not readings:
            return None

        median_value = statistics.median(readings)

        filtered = [
            r for r in readings
            if abs(r - median_value) <= max(5.0, abs(median_value) * 0.10)
        ]

        if not filtered:
            filtered = readings

        stable = statistics.mean(filtered)

        if stable < MIN_VALID_WEIGHT:
            return None

        return stable

    def reset_screen(self):
        if self.busy:
            return

        self.measurements = []
        self.value_label.config(text=f"--.- {DISPLAY_UNIT}", fg="lime")
        self.status_label.config(text="Ready")
        self.progress_label.config(text="")
        self.instruction_label.config(text="Step off the scale and tap ZERO.")

    def quit_app(self, event=None):
        try:
            GPIO.cleanup()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ScaleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
