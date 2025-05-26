import platform
import warnings
import time

# Only import gpiozero on Raspberry Pi (Linux)
if platform.system() == "Linux":
    from gpiozero import DistanceSensor, PWMSoftwareFallback, DistanceSensorNoEcho
else:
    # Mock classes to prevent import errors on macOS or Windows
    class DistanceSensor:
        def __init__(self, *args, **kwargs):
            print("⚠️ DistanceSensor is mocked. No real sensor interaction.")
            self.distance = 0.42  # Return dummy distance value

        def close(self):
            print("⚠️ Closing mocked DistanceSensor")

    PWMSoftwareFallback = type("PWMSoftwareFallback", (), {})
    DistanceSensorNoEcho = type("DistanceSensorNoEcho", (), {})

class Ultrasonic:
    def __init__(self, trigger_pin: int = 27, echo_pin: int = 22, max_distance: float = 3.0):
        warnings.filterwarnings("ignore", category=DistanceSensorNoEcho)
        warnings.filterwarnings("ignore", category=PWMSoftwareFallback)
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance
        self.sensor = DistanceSensor(echo=self.echo_pin, trigger=self.trigger_pin, max_distance=self.max_distance)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_distance(self) -> float:
        try:
            distance = self.sensor.distance * 100
            return round(float(distance), 1)
        except RuntimeWarning as e:
            print(f"Warning: {e}")
            return None

    def close(self):
        self.sensor.close()

if __name__ == '__main__':
    with Ultrasonic() as ultrasonic:
        try:
            while True:
                distance = ultrasonic.get_distance()
                if distance is not None:
                    print(f"Ultrasonic distance: {distance}cm")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nEnd of program")
