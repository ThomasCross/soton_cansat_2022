from gpiozero import CPUTemperature, LoadAverage, DiskUsage

class HealthChecks:
    # ID: -1
    # Type: Raspberry Pi Zero Health Checks

    def __init__(self):
        self.__temp = CPUTemperature()
        self.__load = LoadAverage()
        self.__disk = DiskUsage()

    def get_temp(self):
        return self.__temp.temperature

    def get_load(self):
        return self.__load.load_average

    def get_disk(self):
        return self.__disk.usage
