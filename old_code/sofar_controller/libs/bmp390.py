from machine import I2C, Pin
import struct
import time

# Constants
_BMP390_CHIP_ID = const(0x60)
_REGISTER_CHIPID = const(0x00)
_REGISTER_STATUS = const(0x03)
_REGISTER_PRESSUREDATA = const(0x04)
_REGISTER_TEMPDATA = const(0x07)
_REGISTER_CONTROL = const(0x1B)
_REGISTER_OSR = const(0x1C)
_REGISTER_ODR = const(0x1D)
_REGISTER_CONFIG = const(0x1F)
_REGISTER_CAL_DATA = const(0x31)
_REGISTER_CMD = const(0x7E)

_OSR_SETTINGS = (1, 2, 4, 8, 16, 32)  # pressure and temperature oversampling settings

class BMP390:
    def __init__(self, i2c, address=0x77):
        self._i2c = i2c
        self._address = address
        self._t_fine = None
        self._oss_t = 32  # default temperature oversampling
        self._oss_p = 32  # default pressure oversampling

        chip_id = self._read_byte(_REGISTER_CHIPID)
        if chip_id != _BMP390_CHIP_ID:
            raise RuntimeError(f"Failed to find BMP390! Chip ID 0x{chip_id:x}")
        
        self._read_coefficients()
        self.reset()
        self.sea_level_pressure = 1013.25
        self._wait_time = 0.002
        
        # Set default oversampling
        self.set_oversampling(self._oss_p, self._oss_t)

    def _read_byte(self, register):
        return self._i2c.readfrom_mem(self._address, register, 1)[0]

    def _write_byte(self, register, value):
        self._i2c.writeto_mem(self._address, register, bytes([value]))

    def _read_register(self, register, length):
        return self._i2c.readfrom_mem(self._address, register, length)

    def reset(self):
        self._write_byte(_REGISTER_CMD, 0xB6)

    def _read_coefficients(self):
        coeff = self._read_register(_REGISTER_CAL_DATA, 21)
        coeff = struct.unpack("<HHbhhbbHHbbhbb", coeff)
        
        self._temp_calib = (
            coeff[0] / 2**-8.0,  # T1
            coeff[1] / 2**30.0,  # T2
            coeff[2] / 2**48.0,  # T3
        )
        self._pressure_calib = (
            (coeff[3] - 2**14.0) / 2**20.0,  # P1
            (coeff[4] - 2**14.0) / 2**29.0,  # P2
            coeff[5] / 2**32.0,  # P3
            coeff[6] / 2**37.0,  # P4
            coeff[7] / 2**-3.0,  # P5
            coeff[8] / 2**6.0,   # P6
            coeff[9] / 2**8.0,   # P7
            coeff[10] / 2**15.0, # P8
            coeff[11] / 2**48.0, # P9
            coeff[12] / 2**48.0, # P10
            coeff[13] / 2**65.0, # P11
        )

    def _read(self):
        self._write_byte(_REGISTER_CONTROL, 0x13)

        while self._read_byte(_REGISTER_STATUS) & 0x60 != 0x60:
            time.sleep(self._wait_time)

        data = self._read_register(_REGISTER_PRESSUREDATA, 6)
        adc_p = data[2] << 16 | data[1] << 8 | data[0]
        adc_t = data[5] << 16 | data[4] << 8 | data[3]

        T1, T2, T3 = self._temp_calib
        P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11 = self._pressure_calib

        pd1 = adc_t - T1
        pd2 = pd1 * T2
        temperature = pd2 + (pd1 * pd1) * T3

        pd1 = P6 * temperature
        pd2 = P7 * temperature**2.0
        pd3 = P8 * temperature**3.0
        po1 = P5 + pd1 + pd2 + pd3

        pd1 = P2 * temperature
        pd2 = P3 * temperature**2.0
        pd3 = P4 * temperature**3.0
        po2 = adc_p * (P1 + pd1 + pd2 + pd3)

        pd1 = adc_p**2.0
        pd2 = P9 + P10 * temperature
        pd3 = pd1 * pd2
        pd4 = pd3 + P11 * adc_p**3.0

        pressure = po1 + po2 + pd4

        return pressure, temperature

    @property
    def pressure(self):
        return self._read()[0] / 100

    @property
    def temperature(self):
        return self._read()[1]

    def set_oversampling(self, pressure_oversampling, temperature_oversampling):
        if pressure_oversampling not in _OSR_SETTINGS:
            raise ValueError(f"Invalid pressure oversampling value. Must be one of: {_OSR_SETTINGS}")
        if temperature_oversampling not in _OSR_SETTINGS:
            raise ValueError(f"Invalid temperature oversampling value. Must be one of: {_OSR_SETTINGS}")
        
        self._oss_p = _OSR_SETTINGS.index(pressure_oversampling)
        self._oss_t = _OSR_SETTINGS.index(temperature_oversampling)
        
        osr_reg_value = (self._oss_t << 3) | self._oss_p
        self._write_byte(_REGISTER_OSR, osr_reg_value)

    @property
    def pressure_oversampling(self):
        return _OSR_SETTINGS[self._oss_p]

    @pressure_oversampling.setter
    def pressure_oversampling(self, oversampling):
        self.set_oversampling(oversampling, self.temperature_oversampling)

    @property
    def temperature_oversampling(self):
        return _OSR_SETTINGS[self._oss_t]

    @temperature_oversampling.setter
    def temperature_oversampling(self, oversampling):
        self.set_oversampling(self.pressure_oversampling, oversampling)

