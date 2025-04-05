import cv2
import numpy as np
import configs
import time
from picamera2 import Picamera2

class Camera:

    def __init__(self, csv, probe):
        self.fps = configs.fps
        self.height = configs.height
        self.width = configs.width
        self.csv = csv
        self.probe = probe
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
        self.params = self.__cameraParameters()
        self.camera = self.initializeCam()

    def __cameraParameters(self):

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

        return parameters
    
    def initializeCam(self):

        cam = Picamera2()
        cam.configure(cam.create_video_configuration(main={"format": 'RGB888', "size": (self.width, self.height)}))
        cam.set_controls({"AfMode": 0, "LensPosition": 100000000000})
        cam.start()

        size = cam.capture_metadata()['ScalerCrop'][2:]

        full_res = cam.camera_properties['PixelArraySize']

        for _ in range(40):
            
            cam.capture_metadata()

            size = [int(s * 0.95) for s in size]
            offset = [(r - s) // 2 for r, s in zip(full_res, size)]
            cam.set_controls({"ScalerCrop": offset + size})

        time.sleep(2)
        return cam
    
    def outlineDetection(self, frame, corners, ids):
    
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
            frame = cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 10), font, 1, (0, 255, 255), thickness=1)

        return frame
    
    def capture(self):

        fram = self.camera.capture_array()  
        gray = cv2.cvtColor(fram, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.params)
        frame = self.outlineDetection(fram, corners, ids)

        if ids is not None:

            self.csv.reading_and_writing_sensors(ids, self.probe, 1)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            cv2.imwrite(f"detected_{timestamp}.jpg", frame)

        cv2.imshow("ArUco Detection", frame)

        return frame