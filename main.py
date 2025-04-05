 #  Copyright (c) 2025 João Toppa <j213140@dac.unicamp.br>
 #  
 #   Redistribution and use in source and binary forms, with or without
 #   modification, are permitted provided that the following conditions
 #   are met:
 # 
 #   1. Redistributions of source code must retain the above Copyright
 #      notice, this list of conditions and the following disclaimer.
 #
 #   2. Redistributions in binary form must reproduce the above Copyright
 #      notice, this list of conditions and the following disclaimer in the
 #      documentation and/or other materials provided with the distribution.
 #
 #   3. Neither the name of the authors nor the names of its contributors
 #      may be used to endorse or promote products derived from this
 #      software without specific prior written permission.
 

# IMPORTS FOR PROBES
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
import tables
import camera

#IMPORTS FOR BEE DETECTION
import cv2
import numpy as np

def button_callback(channel):
    page_manager.next()


#SETUP - PROBES

i2c = busio.I2C(SCL, SDA)
bus = smbus.SMBus(1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

GPIO.add_event_detect(17, GPIO.RISING, callback=button_callback, bouncetime=200)

ccs811 = adafruit_ccs811.CCS811(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, 0x76)
mpu9250 = sensors.Accelerometer(configs.DEVICE_ADDRESS, configs.ACCEL_XOUT_H, configs.ACCEL_CONFIG, bus, configs.PWR_MGMT_1)
sensors.Accelerometer.initialize(mpu9250)
probe = sensors.SensorProbe(ccs811, mpu9250, bmp280)

page1 = Pages(1, "Temperatura: ", display, "C", probe.readTemperature)
page2 = Pages(2, "Vibracao: ", display, "m/s2", probe.readAcceleration)
page3 = Pages(3, "ECO2: ", display, "ppm", probe.readECO2)
page4 = Pages(4, "VOL: ", display, "ppb", probe.readVolatile)

page_manager = managerPages(display)
page_manager.push(page1)
page_manager.push(page2)
page_manager.push(page3)
page_manager.push(page4)

last_update_time = time.time()
update_interval = 0.4

#SETUP - CSV

header = "Data,IDs,Temp-C,Temp-F,Humidity,CO2,TVOC\n"

camera_feed_csv = tables.CSVTables(header, "camera_feed")
station_csv = tables.CSVTables(header, "station_feed")

#SETUP - CAMERA

camera_main = camera.Camera(station_csv, probe)

#MAIN LOOP



try:

    while True:
        current_time = time.time()

        if current_time - last_update_time >= update_interval:
            page_manager.update()
            last_update_time = current_time

        station_csv.reading_and_writing_sensors([[0]],probe, current_time)
        camera_main.capture()

finally:
    GPIO.cleanup()
    display.fill(0)
    display.show()
    cv2.destroyAllWindows()
