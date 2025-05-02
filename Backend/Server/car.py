from motor import Ordinary_Car
from servo import Servo
from infrared import Infrared
from adc import ADC
import time
import math

class Car:
    def __init__(self):
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None
        self.car_record_time = time.time()
        self.time_compensate = 3
        self.start()

    def start(self):  
        if self.servo is None:
            self.servo = Servo()
        if self.motor is None:
            self.motor = Ordinary_Car()
        if self.infrared is None:
            self.infrared = Infrared()
        if self.adc is None:
            self.adc = ADC() 

    def close(self):
        self.motor.set_motor_model(0, 0, 0, 0)
        if self.sonic:
            self.sonic.close()
        self.motor.close()
        self.infrared.close()
        self.adc.close_i2c()
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None

    def mode_ultrasonic(self):
        print("[INFO] Ultrasonic mode disabled — no sensor present.")

    def mode_infrared(self):
        if (time.time() - self.car_record_time) > 0.2:
            self.car_record_time = time.time()
            infrared_value = self.infrared.read_all_infrared()
            if infrared_value == 2:
                self.motor.set_motor_model(800, 800, 800, 800)
            elif infrared_value == 4:
                self.motor.set_motor_model(-1500, -1500, 2500, 2500)
            elif infrared_value == 6:
                self.motor.set_motor_model(-2000, -2000, 4000, 4000)
            elif infrared_value == 1:
                self.motor.set_motor_model(2500, 2500, -1500, -1500)
            elif infrared_value == 3:
                self.motor.set_motor_model(4000, 4000, -2000, -2000)
            elif infrared_value == 7:
                self.motor.set_motor_model(0, 0, 0, 0)

    def mode_light(self):
        if (time.time() - self.car_record_time) > 0.2:
            self.car_record_time = time.time()
            self.motor.set_motor_model(0, 0, 0, 0)
            L = self.adc.read_adc(0)
            R = self.adc.read_adc(1)
            if L < 2.99 and R < 2.99:
                self.motor.set_motor_model(600, 600, 600, 600)
            elif abs(L - R) < 0.15:
                self.motor.set_motor_model(0, 0, 0, 0)
            elif L > 3 or R > 3:
                if L > R:
                    self.motor.set_motor_model(-1200, -1200, 1400, 1400)
                elif R > L:
                    self.motor.set_motor_model(1400, 1400, -1200, -1200)

    def mode_rotate(self, n):
        angle = n
        bat_compensate = 7.5 / (self.adc.read_adc(2) * (3 if self.adc.pcb_version == 1 else 2))
        while True:
            W = 2000
            VY = int(2000 * math.cos(math.radians(angle)))
            VX = -int(2000 * math.sin(math.radians(angle)))
            FR = VY - VX + W
            FL = VY + VX - W
            BL = VY - VX - W
            BR = VY + VX + W
            print("rotating")
            self.motor.set_motor_model(FL, BL, FR, BR)
            time.sleep(5 * self.time_compensate * bat_compensate / 1000)
            angle -= 5

def test_car_infrared():
    car = Car()
    try:
        while True:
            car.mode_infrared()
    except KeyboardInterrupt:
        car.close()
        print("\nEnd of program")

def test_car_light():
    car = Car()
    try:
        print("Program is starting...")
        while True:
            car.mode_light()
    except KeyboardInterrupt:
        car.close()
        print("\nEnd of program")

def test_car_rotate():
    car = Car()
    print("Program is starting...")
    try:
        car.mode_rotate(0)
    except KeyboardInterrupt:
        print("\nEnd of program")
        car.motor.set_motor_model(0, 0, 0, 0)
        car.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Parameter error: Please assign the device")
        exit()
    elif sys.argv[1].lower() == 'infrared':
        test_car_infrared()
    elif sys.argv[1].lower() == 'light':
        test_car_light()
    elif sys.argv[1].lower() == 'rotate':
        test_car_rotate()
