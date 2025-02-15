from RPi import GPIO
from board import SCL, SDA
import busio
import time
import adafruit_ssd1306
import adafruit_ccs811
import adafruit_bmp280
import configs
import sensors
import smbus
from screen import * 

def button_callback(channel):

    print("Botao pressionado!")
    page_manager.next()

i2c = busio.I2C(SCL, SDA)
bus = smbus.SMBus(1)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  

display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
#GPIO.add_event_detect(4, GPIO.RISING, callback=button_callback, bouncetime=20)  
ccs811 = adafruit_ccs811.CCS811(i2c)
bme280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, 0x76)
mpu9250 = sensors.Accelerometer(configs.DEVICE_ADDRESS, configs.ACCEL_XOUT_H, configs.ACCEL_CONFIG, bus, configs.PWR_MGMT_1)
sonda = sensors.SensorProbe(ccs811, mpu9250, bme280)

page1 = Pages(1, "Temperatura: ", display, "C", sonda.readTemperature)
page2 = Pages(2, "Umidade: ", display, "%", sonda.readHumidity)
page3 = Pages(3, "Vibracao: ", display, "", sonda.readAcceleration)

page_manager = managerPages(display)
page_manager.push(page1)
page_manager.push(page2)
page_manager.push(page3)

last_update_time = time.time()  
update_interval = 2

try:
     while True:
        current_time = time.time() 

  
        if current_time - last_update_time >= update_interval:
            
            page_manager.update()
            last_update_time = current_time

finally:
    GPIO.cleanup()


display.fill(0)
display.show()
