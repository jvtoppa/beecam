#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leitura de temperatura e umidade a cada 5 segundos com detecção de marcadores ArUco.
"""
import board
import adafruit_dht
import cv2
import numpy as np
import time
from libcamera import controls
from picamera2 import Picamera2, Preview
from gpiozero import CPUTemperature

# Configurações da câmera
width = 150
height = 150
fps = 60

# Abrir o arquivo para registrar os dados
f = open("values.csv", 'w')
f.write('Data,IDs,Temp-C,Temp-F,Humidity\n')

# Inicializar o sensor DHT22
sensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# Inicializar a câmera e o detector ArUco
def initialize_camera():
    cam = Picamera2()  # Usar Picamera2
    ca.start_preview(Preview.QTGL)
    cam.configure(cam.create_video_configuration(main={"format": 'RGB888', "size": (width, height)}))  # Configuração
    

    cam.start()  # Iniciar a captura de vídeo
    time.sleep(1)
    cam.set_controls({"AfMode": 0, "LensPosition": 425})
    return cam

# Função para visualizar a detecção de ArUco
def outlineDetection(frame, corners, ids):
    color = (0, 0, 255)
    color3 = (255, 100, 0)
    font = cv2.FONT_HERSHEY_PLAIN
    fontscale = 0.75
    for i in range(len(ids)):
        corner = corners[i].reshape((4, 2))
        pts = np.array(corner, np.int32)
        pts = pts.reshape((-1, 1, 2))
        center = np.mean(corner, axis=0)
        center_coords = (int(center[0]), int(center[1]))
        ID = str(ids[i][0])

        frame = cv2.polylines(frame, [pts], True, color3, thickness=2)
        frame = cv2.putText(frame, ID, center_coords, font, fontscale, color, thickness=1)

        cpu = CPUTemperature()
        temp = str(cpu.temperature)
        frame = cv2.putText(frame, "CPU Temp: " + temp, (10, 30), font, 1, (0, 255, 255), thickness=1)
        frame = cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 10), font, 1, (0, 255, 255), thickness=1)

    return frame

# Função para capturar e processar a imagem
def capture_frame():
    frame = camera.capture_array()  # Captura da imagem
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converter para escala de cinza
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        # Marcar e visualizar os detectados
        frame = outlineDetection(frame, corners, ids)
    return frame

# Criar o dicionário ArUco
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()

# Inicializar a câmera
camera = initialize_camera()

# Variáveis para controle de leitura a cada 5 segundos
last_reading_time = time.time()  # Armazena o último tempo de leitura
read_interval = 5  # Intervalo de leitura em segundos

# Loop principal de captura de vídeo e detecção
while True:
    # Capturar e processar a imagem da câmera
    frame = capture_frame()

    # Verificar se já se passaram 5 segundos desde a última leitura do sensor
    current_time = time.time()
    if current_time - last_reading_time >= read_interval:
        try:
            # Realizar a leitura da temperatura e umidade
            temperature_c = sensor.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = sensor.humidity
            print("Temp={0:0.1f}°C, Temp={1:0.1f}°F, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))

            # Escrever os dados no arquivo CSV
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{temperature_c},{temperature_f},{humidity}\n")

        except RuntimeError as error:
            # Erro de leitura, continuar tentando
            print(error.args[0])

        # Atualizar o tempo da última leitura
        last_reading_time = current_time

    # Exibir o frame com as tags detectadas
    cv2.imshow("ArUco Detection", frame)

    # Interromper quando a tecla 'ESC' for pressionada
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Fechar tudo adequadamente
camera.stop()  # Parar a captura da câmera
cv2.destroyAllWindows()
f.close()  # Fechar o arquivo CSV
