import time

# Try importing gpiozero for real hardware support
try:
    from gpiozero import LineSensor
    HARDWARE_AVAILABLE = True
except ImportError:
    print("[WARN] gpiozero not available — hardware features disabled.")
    HARDWARE_AVAILABLE = False

# Define the Infrared class to manage infrared sensors
class Infrared:
    def __init__(self):
        self.IR_PINS = {
            1: 14,
            2: 15,
            3: 23
        }

        if HARDWARE_AVAILABLE:
            self.sensors = {
                channel: LineSensor(pin)
                for channel, pin in self.IR_PINS.items()
            }
        else:
            self.sensors = {}  # No hardware, no sensors

    def read_one_infrared(self, channel: int) -> int:
        """Read the value of a single infrared sensor."""
        if not HARDWARE_AVAILABLE:
            print(f"[SIM] Reading infrared sensor {channel}: returning 0")
            return 0

        if channel in self.sensors:
            return 1 if self.sensors[channel].value else 0
        else:
            raise ValueError(f"Invalid channel: {channel}. Valid channels are {list(self.IR_PINS.keys())}.")

    def read_all_infrared(self) -> int:
        """Combine the values of all three infrared sensors into a single integer."""
        return (self.read_one_infrared(1) << 2) | (self.read_one_infrared(2) << 1) | self.read_one_infrared(3)

    def close(self) -> None:
        """Close all sensors if available."""
        if HARDWARE_AVAILABLE:
            for sensor in self.sensors.values():
                sensor.close()

# Main entry point for testing the Infrared class
if __name__ == '__main__':
    infrared = Infrared()
    try:
        while True:
            value = infrared.read_all_infrared()
            print(f"Infrared value: {value}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        infrared.close()
        print("\nEnd of program")
