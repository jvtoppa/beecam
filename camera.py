import cv2
import numpy as np
import configs
import time
from picamera2 import Picamera2
import tables


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
        parameters = cv2.aruco.DetectorParameters_create()
        parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        return parameters

    def initializeCam(self):
        cam = Picamera2()

        print("[DEBUG] Configurando camera para preview simples")
        cam.configure(cam.create_preview_configuration(main={"format": 'RGB888', "size": (self.width, self.height)}))

        print("[DEBUG] Iniciando camera")
        cam.start()

        time.sleep(2)  # dempo pro sensor ajustar

        return cam

    def outlineDetection(self, frame, corners, ids):
        if ids is not None:
            color = (0, 0, 255)
            color3 = (255, 100, 0)
            font = cv2.FONT_HERSHEY_PLAIN
            fontscale = 0.75

            for i in range(len(ids)):
                corner = corners[i].reshape((4, 2))
                pts = np.array(corner, np.int32).reshape((-1, 1, 2))
                center = np.mean(corner, axis=0).astype(int)
                ID = str(ids[i][0])
                cv2.polylines(frame, [pts], True, color3, 2)
                cv2.putText(frame, ID, tuple(center), font, fontscale, color, 1)

            cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 10), font, 1, (0, 255, 255), 1)

        return frame

    def capture(self):
        fram = self.camera.capture_array()
        curr = time.time()
        print("[DEBUG] Frame capturado, shape:", fram.shape)

        gray = cv2.cvtColor(fram, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.params)
        frame = self.outlineDetection(fram, corners, ids)

        if ids is not None:
            print("[DEBUG] Marcadores detectados:", ids.flatten())
            self.csv.reading_and_writing_sensors(ids, self.probe, curr)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            cv2.imwrite(f"detected_{timestamp}.jpg", frame)

        cv2.imshow("ArUco Detection", frame)
        return frame
