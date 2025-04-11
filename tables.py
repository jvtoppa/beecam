import configs
import time

class CSVTables:

    def __init__(self, typ, header, interval):
        self.pathCSV = configs.path_to_folder + time.strftime('%Y-%m-%d-%H:%M:%S_') + typ + ".csv"
        self.headerCSV = header
        self.last_read_time = 0
        self.read_interval = interval
        self.initialize()


    def initialize(self):
        self.csv = open(self.pathCSV, 'w')
        self.csv.write(self.headerCSV + "\n")


    def reading_and_writing_sensors(self, ids, probe, current_time):
        if current_time - self.last_read_time >= self.read_interval:
            temperature_c = probe.readTemperature()

            if not isinstance(temperature_c, str):
                temperature_f = temperature_c * (9 / 5) + 32
                temperature_c = round(temperature_c, 2)
                temperature_f = round(temperature_f, 2)

            co2 = probe.readECO2()
            tvoc = probe.readVolatile()
            vibration = probe.readAcceleration()

            self.csv.write(f"{time.strftime('%Y-%m-%d-%H:%M:%S')},{ids[0][0]},{temperature_c},{temperature_f},{co2},{tvoc},{vibration}\n")
            self.csv.flush()

            self.last_read_time = current_time


    def __del__(self):
        if hasattr(self, 'csv') and not self.csv.closed:
            self.csv.close()
