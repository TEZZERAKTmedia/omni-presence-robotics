import time
from servo import Servo

def test_servo_speeds():
    # Instantiate the servo controller
    servo_controller = Servo()  
    channel = '2'  # Replace with the appropriate channel

    print("Starting Servo Speed Tests...")
    print("Using channel:", channel)

    # Define a range of PWM values.
    # For a continuous rotation servo, 1500 typically means "stop".
    # Values lower than 1500 will make it spin one way (e.g., left),
    # and values higher than 1500 will spin it the opposite way (e.g., right).
    # Adjust these values according to your servo's specifications.
    left_speeds = [1500, 1400, 1300, 1200, 1100, 1000, 900]   # Lower than 1500 = left turn
    right_speeds = [1500, 1600, 1700, 1800, 1900, 2000, 2100]  # Higher than 1500 = right turn

    # Test left direction speeds:
    print("\nTesting Left Direction:")
    for pulse in left_speeds:
        print(f"Left Test: Setting pulse width to {pulse}")
        servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], pulse)
        time.sleep(2)  # Pause so you can observe the change

    # Bring the servo to a stop before switching directions
    print("\nStopping Servo...")
    servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], 1500)
    time.sleep(2)

    # Test right direction speeds:
    print("\nTesting Right Direction:")
    for pulse in right_speeds:
        print(f"Right Test: Setting pulse width to {pulse}")
        servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], pulse)
        time.sleep(2)

    # Final stop command
    print("\nFinal Stop")
    servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], 1500)
    print("Done testing!")

if __name__ == '__main__':
    test_servo_speeds()
