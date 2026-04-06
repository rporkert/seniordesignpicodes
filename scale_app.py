#!/usr/bin/env python3
import time
import statistics
import tkinter as tk
import RPi.GPIO as GPIO
from hx711 import HX711

DATA_PIN = 17
CLOCK_PIN = 27

OFFSET = 0
SCALE_FACTOR = 1000.0
DISPLAY_UNIT = "lb"

SETTLE_TIME_SECONDS = 1.5
MEASUREMENT_TIME_SECONDS = 2.5
SAMPLE_DELAY_SECONDS = 0.08
MIN_VALID_WEIGHT = 20.0

HX711_CHANNEL = "A"
HX711_GAIN = 128


class ScaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Touch Scale")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.quit_app)

        self.hx = None
        self.busy = False
        self.measurements = []

        self.build_ui()
        self.show_startup_status()

    def show_startup_status(self):
        self.value_label.config(text=f"--.- {DISPLAY_UNIT}", fg="lime")
        self.status_label.config(text="App started")
        self.instruction_label.config(
            text="Tap CONNECT SENSOR after wiring the HX711, or test the screen now"
        )

    def build_ui(self):
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        self.header_label = tk.Label(
            self.main_frame,
            text="DIGITAL SCALE",
            font=("Arial", 26, "bold"),
            fg="white",
            bg="black"
        )
        self.header_label.pack(pady=(18, 8))

        self.instruction_label = tk.Label(
            self.main_frame,
            text="Loading...",
            font=("Arial", 20, "bold"),
            fg="cyan",
            bg="black",
            wraplength=760,
            justify="center"
        )
        self.instruction_label.pack(pady=(5, 10))

        self.value_label = tk.Label(
            self.main_frame,
            text=f"--.- {DISPLAY_UNIT}",
            font=("Arial", 58, "bold"),
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

        self.connect_button = tk.Button(
            button_frame,
            text="CONNECT\nSENSOR",
            font=("Arial", 22, "bold"),
            width=10,
            height=3,
            command=self.connect_sensor,
            bg="#6a1b9a",
            fg="white",
            bd=4
        )
        self.connect_button.grid(row=0, column=0, padx=12, pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="START\nMEASUREMENT",
            font=("Arial", 24, "bold"),
            width=14,
            height=3,
            command=self.start_measurement,
            bg="#1976d2",
            fg="white",
            activebackground="#125ca1",
            activeforeground="white",
            bd=4
        )
        self.start_button.grid(row=0, column=1, padx=12, pady=10)

        self.zero_button = tk.Button(
            button_frame,
            text="ZERO /\nTARE",
            font=("Arial", 22, "bold"),
            width=10,
            height=3,
            command=self.zero_scale,
            bg="#424242",
            fg="white",
            activebackground="#303030",
            activeforeground="white",
            bd=4
        )
        self.zero_button.grid(row=0, column=2, padx=12, pady=10)

        self.remeasure_button = tk.Button(
            button_frame,
            text="RE-\nMEASURE",
            font=("Arial", 22, "bold"),
            width=10,
            height=3,
            command=self.reset_screen,
            bg="#2e7d32",
            fg="white",
            activebackground="#205723",
            activeforeground="white",
            bd=4
        )
        self.remeasure_button.grid(row=0, column=3, padx=12, pady=10)

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

    def connect_sensor(self):
        if self.busy:
            return

        self.status_label.config(text="Connecting to HX711...")
        self.progress_label.config(text="")
        self.root.update()

        try:
            if self.hx is not None:
                try:
                    GPIO.cleanup()
                except Exception:
                    pass
                self.hx = None

            self.hx = HX711(
                dout_pin=DATA_PIN,
                pd_sck_pin=CLOCK_PIN,
                channel=HX711_CHANNEL,
                gain=HX711_GAIN
            )
            self.hx.reset()
            time.sleep(0.2)

            self.status_label.config(text="HX711 connected")
            self.instruction_label.config(
                text="Tap ZERO with nobody on the scale, then START MEASUREMENT"
            )
        except Exception as e:
            self.hx = None
            self.status_label.config(text=f"HX711 connection failed: {e}")
            self.instruction_label.config(
                text="If the HX711 is not wired yet, this is expected"
            )

    def set_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.connect_button.config(state=state)
        self.start_button.config(state=state)
        self.zero_button.config(state=state)
        self.remeasure_button.config(state=state)

    def read_raw_once(self):
        if self.hx is None:
            raise RuntimeError("HX711 not connected. Tap CONNECT SENSOR first.")

        values = self.hx.get_raw_data(num_measures=3)
        if not values:
            raise RuntimeError("No HX711 data returned")

        int_values = [int(v) for v in values]
        return statistics.median(int_values)

    def raw_to_display_units(self, raw_value):
        return (raw_value - OFFSET) / SCALE_FACTOR

    def zero_scale(self):
        if self.hx is None or self.busy:
            if self.hx is None:
                self.status_label.config(text="Connect the sensor first")
            return

        self.busy = True
        self.set_buttons_enabled(False)
        self.status_label.config(text="Zeroing scale... Make sure nobody is standing on it.")
        self.progress_label.config(text="")
        self.instruction_label.config(text="Please step off the scale")
        self.root.update()

        try:
            time.sleep(1.5)
            zero_samples = []
            for _ in range(10):
                zero_samples.append(self.read_raw_once())
                time.sleep(0.05)

            zero_raw = statistics.median(zero_samples)

            self.value_label.config(text=f"0.0 {DISPLAY_UNIT}")
            self.status_label.config(text=f"Current empty raw value: {zero_raw}")
            self.instruction_label.config(
                text="For permanent tare, copy this raw value into OFFSET later"
            )
        except Exception as e:
            self.status_label.config(text=f"Zero failed: {e}")
        finally:
            self.busy = False
            self.set_buttons_enabled(True)

    def reset_screen(self):
        if self.busy:
            return

        self.measurements = []
        self.value_label.config(text=f"--.- {DISPLAY_UNIT}", fg="lime")
        self.status_label.config(text="Ready")
        self.progress_label.config(text="")
        self.instruction_label.config(text="Tap CONNECT SENSOR, then measure")

    def start_measurement(self):
        if self.hx is None or self.busy:
            if self.hx is None:
                self.status_label.config(text="Connect the sensor first")
            return

        self.busy = True
        self.measurements = []
        self.set_buttons_enabled(False)

        self.instruction_label.config(text="Stand still while measuring")
        self.status_label.config(text="Preparing measurement...")
        self.progress_label.config(text="Settling...")
        self.value_label.config(text="...", fg="yellow")
        self.root.update()

        try:
            time.sleep(SETTLE_TIME_SECONDS)

            start_time = time.time()
            count = 0

            while (time.time() - start_time) < MEASUREMENT_TIME_SECONDS:
                raw_value = self.read_raw_once()
                scaled_value = self.raw_to_display_units(raw_value)
                self.measurements.append(scaled_value)
                count += 1

                self.value_label.config(text=f"{scaled_value:.1f} {DISPLAY_UNIT}", fg="yellow")
                self.status_label.config(text="Measuring... please stand still")
                self.progress_label.config(text=f"Samples collected: {count}")
                self.root.update()

                time.sleep(SAMPLE_DELAY_SECONDS)

            stable_weight = self.compute_stable_weight(self.measurements)

            if stable_weight is None:
                self.value_label.config(text="NO LOAD", fg="orange")
                self.status_label.config(text="No valid weight detected")
                self.instruction_label.config(text="Step on the scale and try again")
                self.progress_label.config(text="")
            else:
                self.value_label.config(text=f"{stable_weight:.1f} {DISPLAY_UNIT}", fg="lime")
                self.status_label.config(text="Measurement complete")
                self.instruction_label.config(text="Please step off the scale")
                self.progress_label.config(text="Tap RE-MEASURE for the next reading")

        except Exception as e:
            self.value_label.config(text="ERROR", fg="red")
            self.status_label.config(text=f"Measurement failed: {e}")
            self.instruction_label.config(text="Check HX711 connection and calibration")
            self.progress_label.config(text="")
        finally:
            self.busy = False
            self.set_buttons_enabled(True)

    def compute_stable_weight(self, readings):
        if not readings:
            return None

        median_value = statistics.median(readings)
        filtered = []

        for r in readings:
            if abs(r - median_value) <= max(2.0, abs(median_value) * 0.05):
                filtered.append(r)

        if not filtered:
            filtered = readings

        stable = statistics.mean(filtered)

        if stable < MIN_VALID_WEIGHT:
            return None

        return stable

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
