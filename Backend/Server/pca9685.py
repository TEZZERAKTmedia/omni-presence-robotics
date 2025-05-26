#!/usr/bin/python

import time
import math

try:
    import smbus2
    I2C_AVAILABLE = True
except ImportError:
    print("[WARN] smbus2 not available — PWM features disabled.")
    smbus2 = None
    I2C_AVAILABLE = False

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:
    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address: int = 0x40, debug: bool = False):
        self.address = address
        self.debug = debug
        self.bus = None

        if I2C_AVAILABLE:
            try:
                self.bus = smbus2.SMBus(1)
                self.write(self.__MODE1, 0x00)
            except FileNotFoundError:
                print("[WARN] /dev/i2c-1 not found — PCA9685 disabled.")
                self.bus = None

    def write(self, reg: int, value: int) -> None:
        if self.bus:
            self.bus.write_byte_data(self.address, reg, value)

    def read(self, reg: int) -> int:
        if self.bus:
            return self.bus.read_byte_data(self.address, reg)
        return 0

    def set_pwm_freq(self, freq: float) -> None:
        if not self.bus:
            return
        prescaleval = 25000000.0 / 4096.0 / float(freq) - 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)
        self.write(self.__PRESCALE, int(prescale))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def set_pwm(self, channel: int, on: int, off: int) -> None:
        if not self.bus:
            return
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)

    def set_motor_pwm(self, channel: int, duty: int) -> None:
        self.set_pwm(channel, 0, duty)

    def set_servo_pulse(self, channel: int, pulse: float) -> None:
        pwm_val = pulse * 4096 / 20000
        self.set_pwm(channel, 0, int(pwm_val))

    def close(self) -> None:
        if self.bus:
            self.bus.close()

if __name__ == '__main__':
    print("PCA9685 module loaded.")
