import time
from parameter import ParameterManager

try:
    import smbus2
    I2C_AVAILABLE = True
except ImportError:
    print("[WARN] smbus2 not available — I2C features disabled.")
    smbus2 = None
    I2C_AVAILABLE = False

class ADC:
    def __init__(self):
        """Initialize the ADC class."""
        self.I2C_ADDRESS = 0x48
        self.ADS7830_COMMAND = 0x84
        self.parameter_manager = ParameterManager()
        self.pcb_version = self.parameter_manager.get_pcb_version()
        self.adc_voltage_coefficient = 3.3 if self.pcb_version == 1 else 5.2

        if I2C_AVAILABLE:
            try:
                self.i2c_bus = smbus2.SMBus(1)
            except FileNotFoundError:
                print("[WARN] /dev/i2c-1 not found — I2C bus not initialized.")
                self.i2c_bus = None
        else:
            self.i2c_bus = None

    def _read_stable_byte(self) -> int:
        if not self.i2c_bus:
            return 0
        while True:
            value1 = self.i2c_bus.read_byte(self.I2C_ADDRESS)
            value2 = self.i2c_bus.read_byte(self.I2C_ADDRESS)
            if value1 == value2:
                return value1

    def read_adc(self, channel: int) -> float:
        if not self.i2c_bus:
            return 0.0
        command_set = self.ADS7830_COMMAND | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
        self.i2c_bus.write_byte(self.I2C_ADDRESS, command_set)
        value = self._read_stable_byte()
        voltage = value / 255.0 * self.adc_voltage_coefficient
        return round(voltage, 2)

    def scan_i2c_bus(self) -> None:
        if not self.i2c_bus:
            print("[INFO] I2C not available.")
            return
        print("Scanning I2C bus...")
        for device in range(128):
            try:
                self.i2c_bus.read_byte_data(device, 0)
                print(f"Device found at address: 0x{device:02X}")
            except OSError:
                pass

    def close_i2c(self) -> None:
        if self.i2c_bus:
            self.i2c_bus.close()

if __name__ == '__main__':
    print('Program is starting...')
    adc = ADC()
    try:
        while True:
            left_idr = adc.read_adc(0)
            right_idr = adc.read_adc(1)
            power = adc.read_adc(2) * (3 if adc.pcb_version == 1 else 2)
            print(f"Left IDR: {left_idr}V, Right IDR: {right_idr}V, Power: {power}V")
            time.sleep(1)
    except KeyboardInterrupt:
        adc.close_i2c()
