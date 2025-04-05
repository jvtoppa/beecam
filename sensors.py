import smbus
import board
import busio
from time import sleep
import adafruit_ccs811
import adafruit_bme280

class Accelerometer:

    def __init__(self, deviceAddress, xByteOutHigh, deviceConfig, i2cBus, powerManager):
        self.addr = deviceAddress
        self.xH = xByteOutHigh
        self.devConfg = deviceConfig
        self.bus = i2cBus
        self.pwrMgr = powerManager
        self.alpha = 0.9
        self.last = [0.0, 0.0, 0.0]
        self.hp = [0.0, 0.0, 0.0]
        self.initialize()
    
    def initialize(self):
        self.bus.write_byte_data(self.addr, self.pwrMgr, 0x00)
        sleep(0.1)
        self.bus.write_byte_data(self.addr, self.devConfg, 0x00)
        
    def readRaw(self, addr):
        high = self.bus.read_byte_data(self.addr, addr)
        low = self.bus.read_byte_data(self.addr, addr + 1)
        value = (high << 8) | low
        if value > 32767:
            value -= 65536
        return value

    def readVibration(self):
        base_addr = self.xH
        axes = [0.0, 0.0, 0.0]
        for i in range(3):
            raw = self.readRaw(base_addr + 2*i)
            g = raw / 16384.0
            self.hp[i] = self.alpha * (self.hp[i] + g - self.last[i])
            self.last[i] = g
            axes[i] = self.hp[i] * 9.81
        vib_total = (axes[0]**2 + axes[1]**2 + axes[2]**2) ** 0.5
        return vib_total



class SensorProbe:
    def __init__(self, ccs811, mpu9250, bme280):
        self.vo2 = ccs811
        self.accel = mpu9250
        self.humTemp = bme280

    def readECO2(self):
        if self.vo2:
            try:
                return self.vo2.eco2
            except Exception as e:
                print("Could not read eCO2 - " , e)
                return "N/A"
        else:
            return "N/A"
        
    def readVolatile(self):
        if self.vo2:
            try:
                return self.vo2.tvoc
            except Exception as e:
                print("Could not read TVOC - ", e)
                return "N/A"
        else:
            return "N/A"
        
    def readHumidity(self):
        if self.humTemp:
            try:
                return self.humTemp.humidity
            except Exception as e:
                print("Could not read humidity values - ", e)
                return "N/A"
        else:
            return "N/A"
        
    def readTemperature(self):
        if self.humTemp:
            try:
                return self.humTemp.temperature
            except Exception as e:
                print("Could not read temperature - ", e)
                return "N/A"
        else:
            return "N/A"
        
    
    def readAcceleration(self):
        if self.accel:
            try:
                return self.accel.readVibration()
            except Exception as e:
                print("Could not read vibration - ", e)
                return "N/A"
        else:
            return "N/A"
        
