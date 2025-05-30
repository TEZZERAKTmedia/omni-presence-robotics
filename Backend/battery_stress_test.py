from Server.car import Car
import time

def run_battery_stress_test():
    print("[Battery Test] Starting stress test. Press Ctrl+C to stop.")
    car = Car(enable_adc=False, enable_infrared=False)

    try:
        pan_position = 60
        tilt_position = 60
        pan_direction = 1
        tilt_direction = 1

        while True:
            # Run motors at 50%
            car.motor.set_motor_model(1500, 1500, 1500, 1500)

            # Oscillate servo 0 (pan)
            car.servo.set_servo_pwm('0', pan_position)
            pan_position += 5 * pan_direction
            if pan_position >= 120 or pan_position <= 60:
                pan_direction *= -1

            # Oscillate servo 1 (tilt)
            car.servo.set_servo_pwm('1', tilt_position)
            tilt_position += 5 * tilt_direction
            if tilt_position >= 120 or tilt_position <= 60:
                tilt_direction *= -1

            # Sleep briefly to simulate real-time control loop
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n[Battery Test] Stopping test.")
        car.motor.set_motor_model(0, 0, 0, 0)
        car.close()

if __name__ == "__main__":
    run_battery_stress_test()
