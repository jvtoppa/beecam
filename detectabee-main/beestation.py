#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import board
import adafruit_dht
import cv2
import numpy as np
import time
from picamera2 import Picamera2
from gpiozero import CPUTemperature
import adafruit_ccs811
import busio

# Configurações da câmera
width = 300
height = 300
fps = 120

# Arquivos para gravar os dados
f = open("/home/neepc/Desktop/dht_test/dht22/" + str(time.strftime('%Y-%m-%d-%H:%M:%S')) + "_camera.csv", 'w')
g = open("/home/neepc/Desktop/dht_test/dht22/" + str(time.strftime('%Y-%m-%d-%H:%M:%S')) + "_station.csv", 'w')
f.write("Data,IDs,Temp-C,Temp-F,Humidity,CO2,TVOC\n")
g.write("Data,IDs,Temp-C,Temp-F,Humidity,CO2,TVOC\n")

# Inicializar sensores
sensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)
i2c = busio.I2C(board.SCL, board.SDA)
ccs811 = adafruit_ccs811.CCS811(i2c)

# Função para visualizar a detecção da ArUco
def outlineDetection(frame, corners, ids):
    # Verificar se os IDs são válidos (não são None)
    if ids is not None:
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

            # Adicionar informações de CPU e tempo
            cpu = CPUTemperature()
            temp = str(cpu.temperature)
            frame = cv2.putText(frame, "CPU Temp: " + temp, (10, 30), font, 1, (0, 255, 255), thickness=1)
            frame = cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 10), font, 1, (0, 255, 255), thickness=1)

    return frame


# Inicializar a câmera e o detector ArUco
def initialize_camera():
    cam = Picamera2()
    cam.configure(cam.create_video_configuration(main={"format": 'RGB888', "size": (width, height)}))
    cam.set_controls({"AfMode": 0, "LensPosition": 100000000000})
    cam.start()

    size = cam.capture_metadata()['ScalerCrop'][2:]

    full_res = cam.camera_properties['PixelArraySize']

    for _ in range(40):
        # This syncs us to the arrival of a new camera frame:
        cam.capture_metadata()

        size = [int(s * 0.95) for s in size]
        offset = [(r - s) // 2 for r, s in zip(full_res, size)]
        cam.set_controls({"ScalerCrop": offset + size})

    time.sleep(2)
    return cam

# Função para realizar as leituras a cada 5 segundos
def leitura(ids, fil, last_read_time, read_interval):
    current_time = time.time()

    # Verificar se o intervalo de leitura foi alcançado
    if current_time - last_read_time >= read_interval:
        try:
            # Ler o sensor DHT22
            temperature_c = sensor.temperature
            humidity = sensor.humidity
            if temperature_c is not None and humidity is not None:
                temperature_f = temperature_c * (9 / 5) + 32
                temperature_c = round(temperature_c, 1)
                temperature_f = round(temperature_f, 1)
                humidity = round(humidity, 1)

                if ccs811.data_ready:  # Verifica se os dados estão prontos
                    co2 = ccs811.eco2  # Leitura de CO2
                    tvoc = ccs811.tvoc  # Leitura de TVOC
                    fil.write(f"{time.strftime('%Y-%m-%d-%H:%M:%S')},{ids[0][0]},{temperature_c},{temperature_f},{humidity},{co2},{tvoc}\n")
                    fil.flush()  # Forçar a escrita no arquivo imediatamente
                    
                    print(f"CO2: {co2} ppm")
                    print(f"TVOC: {tvoc} ppb")
                else:
                    fil.write(f"{time.strftime('%Y-%m-%d-%H:%M:%S')},{ids[0][0]},{temperature_c},{temperature_f},{humidity},N/A,N/A\n")
                    fil.flush()  # Forçar a escrita no arquivo imediatamente
        except RuntimeError as error:
            print("Erro de leitura do DHT:", error.args[0])

        # Atualizar o tempo da última leitura
        last_read_time = current_time

    return last_read_time


# Criar o dicionário ArUco
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco_DetectorParameters.create()


parameters.adaptiveThreshWinSizeMin = 5  # Janela mínima mais alta para reduzir detecção de ruído
parameters.adaptiveThreshWinSizeMax = 35  # Janela máxima mais ampla para maior tolerância
parameters.adaptiveThreshConstant = 7  # Constante de adaptação para mais precisão

parameters.minMarkerPerimeterRate = 0.02  # Aumenta um pouco o perímetro mínimo dos marcadores
parameters.maxMarkerPerimeterRate = 4.0  # Ajuste para permitir variações maiores no tamanho
parameters.perspectiveRemovePixelPerCell = 4  # Aumentar para maior precisão de remoção de distorções
parameters.perspectiveRemoveIgnoredMarginPerCell = 0.15  # Ajuste para maior margem de tolerância
parameters.errorCorrectionRate = 0.6  # Tolerância maior para correção de erro
parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX  # Refinamento de canto para maior precisão

parameters.maxErroneousBitsInBorderRate = 0.1
parameters.minDistanceToBorder = 5
parameters.cornerRefinementWinSize = 5
parameters.cornerRefinementMaxIterations = 30


# Inicializar a câmera
camera = initialize_camera()

read_interval = 5  # Intervalo de leitura de sensores (5 segundos)
last_read_time = time.time()  # Controla o tempo de leitura do sensor DHT

# Loop principal de captura de vídeo e detecção
try:
    while True:
        # Captura da imagem
        fram = camera.capture_array()  
        gray = cv2.cvtColor(fram, cv2.COLOR_BGR2GRAY)  # Converter para escala de cinza

        # Detectar os marcadores ArUco
        corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        frame = outlineDetection(fram, corners, ids)

        # Realizar a leitura do sensor DHT e CCS811 a cada 5 segundos
        last_read_time = leitura([[0]], g, last_read_time, read_interval)

        if ids is not None:
            # Marcar e visualizar os detectados
            leitura(ids, f, last_read_time, 1)

        # Exibir o frame com as tags detectadas
        cv2.imshow("ArUco Detection", frame)

        # Interromper quando a tecla 'ESC' for pressionada
        if cv2.waitKey(1) & 0xFF == 27:
            break
except KeyboardInterrupt:
    pass
finally:
    # Fechar tudo adequadamente
    f.close()
    g.close()
    cv2.destroyAllWindows()
    camera.stop()
