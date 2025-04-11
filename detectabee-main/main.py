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
import board
import busio
import time
import adafruit_ssd1306
import adafruit_ccs811
import adafruit_am2320
import configs
import sensors
import smbus
from screen import *
import tables
import camera
import memorystick

#IMPORTS FOR BEE DETECTION
import cv2
import numpy as np

def button_page(channel):
    page_manager_sensors_1.next()

def button_memory_stick(channel):
    global memorystick_start_time, showing_memorystick_message
    memorystick_start_time = time.time()
    showing_memorystick_message = True
    memorystick.copy_to_stick(page_manager_memorystick)
    memorystick_start_time = time.time()

#SETUP - I2C and DISPLAYS

def init_display_and_bus(bus_num):
    if bus_num == 0:
        scl = board.GPIO1
        sda = board.GPIO0
    elif bus_num == 1:
        scl = board.SCL
        sda = board.SDA
    else:
        raise ValueError("Barramento I2C invalido")

    i2c = busio.I2C(scl, sda)
    bus = smbus.SMBus(bus_num)
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    return i2c, bus, display

i2c0, bus0, display0 = init_display_and_bus(0)
i2c1, bus1, display1 = init_display_and_bus(1)

#SETUP - GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.output(5, GPIO.HIGH)
GPIO.output(17, GPIO.HIGH)
GPIO.add_event_detect(23, GPIO.RISING, callback=button_page, bouncetime=200)
GPIO.add_event_detect(24, GPIO.RISING, callback=button_memory_stick, bouncetime=200)

#SETUP - Sensores

ccs811_0 = adafruit_ccs811.CCS811(i2c0)
am2320_0 = adafruit_am2320.AM2320(i2c0)
probe_0 = sensors.SensorProbe(ccs811_0, "", am2320_0)

am2320_1 = adafruit_am2320.AM2320(i2c0)
mpu9250_1 = sensors.Accelerometer(configs.DEVICE_ADDRESS, configs.ACCEL_XOUT_H, configs.ACCEL_CONFIG, bus0, configs.PWR_MGMT_1)
ccs811_1 = adafruit_ccs811.CCS811(i2c1)
probe_1 = sensors.SensorProbe(ccs811_1, mpu9250_1, am2320_1)

#SETUP - Pages

page_manager_sensors_1 = managerPages(display1)

page_manager_sensors_1.push(Pages(1, "[INTERNO] Temperatura: ", display1, "C", probe_1.readTemperature))
page_manager_sensors_1.push(Pages(2, "[INTERNO] Vibracao: ", display1, "m/s2", probe_1.readAcceleration))
page_manager_sensors_1.push(Pages(3, "[INTERNO] ECO2: ", display1, "ppm", probe_1.readECO2))
page_manager_sensors_1.push(Pages(4, "[INTERNO] VOL: ", display1, "ppb", probe_1.readVolatile))
page_manager_sensors_1.push(Pages(5, "[INTERNO] Humidade: ", display1, "%", probe_1.readHumidity))
page_manager_sensors_1.push(Pages(6, "[EXTERNO] Temperatura: ", display1, "C", probe_0.readTemperature))
page_manager_sensors_1.push(Pages(7, "[EXTERNO] ECO2: ", display1, "ppm", probe_0.readECO2))
page_manager_sensors_1.push(Pages(8, "[EXTERNO] VOL: ", display1, "ppb", probe_0.readVolatile))
page_manager_sensors_1.push(Pages(9, "[EXTERNO] Humidade: ", display1, "ppb", probe_0.readHumidity))

page_manager_memorystick = managerPages(display1)

page_manager_memorystick.push(Pages(1, "[ERRO] Nenhum pendrive encontrado.", display1, "", ""))
page_manager_memorystick.push(Pages(2, "[INFO] Nenhum arquivo para copiar.", display1, "", ""))
page_manager_memorystick.push(Pages(3, "[OK] Pendrive pode ser removido com seguranca.", display1, "", ""))
page_manager_memorystick.push(Pages(4, "[ERRO] Falha ao desmontar o pendrive.", display1, "", ""))
page_manager_memorystick.push(Pages(5, "[ERRO] Falha ao copiar", display1, "", ""))

last_update_time = time.time()
update_interval = 0.4
memorystick_start_time = 0
memorystick_duration = 4
showing_memorystick_message = False

#SETUP - CSV
header = "Data,IDs,Temp-C,Temp-F,CO2,TVOC,Vibration\n"
camera_feed_csv = tables.CSVTables("camera_feed", header, 5)
station_csv = tables.CSVTables("station_feed", header, 1)

#SETUP - CAMERA
camera_main = camera.Camera(camera_feed_csv, probe_1)

#MAIN LOOP
try:
    while True:
        current_time = time.time()

        if current_time - last_update_time >= update_interval:

            page_manager_sensors_1.update()
            last_update_time = current_time

        if showing_memorystick_message:
            if current_time - memorystick_start_time >= memorystick_duration:
                display1.fill(0)
                display1.show()
                showing_memorystick_message = False

        station_csv.reading_and_writing_sensors([[0]], probe_0, current_time)
        camera_main.capture()

finally:
    GPIO.cleanup()
    display1.fill(0)
    display1.show()
    cv2.destroyAllWindows()
