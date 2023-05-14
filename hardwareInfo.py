import os
import wmi
import clr
import psutil
import win32pdh

dll_path = os.path.join(os.getcwd(), "OpenHardwareMonitorLib.dll")

if not os.path.exists(dll_path):
    raise Exception(f"Could not find file: {dll_path}")

clr.AddReference(dll_path)
# e.g. clr.AddReference(r'OpenHardwareMonitor/OpenHardwareMonitorLib'), without .dll

from OpenHardwareMonitor.Hardware import Computer


class HardWare:
    def __init__(self):
        computer = Computer()
        computer.MainboardEnabled = True
        computer.CPUEnabled = True
        computer.GPUEnabled = True
        computer.FanControllerEnabled = True
        computer.HDDEnabled = True
        computer.RAMEnabled = True
        computer.Open()
        print("Available hardware in OpenHardwareMonitor:")
        for hardware in computer.Hardware:
            print(f"Hardware: {hardware.Name}, Type: {hardware.HardwareType}")
            for sensor in hardware.Sensors:
                print(f"\tSensor: {sensor.Name}, Type: {sensor.SensorType}")

        self.hardware = computer.Hardware
        #  Sensor: GPU Memory Total
        for hardware in self.hardware:
            if str(hardware.HardwareType) == 'RAM':
                for sensor in hardware.Sensors:
                    if str(sensor.Name) == 'Available Memory':
                        hardware.Update()
                        self.total_ram_memory = sensor.Value


    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_gpu_usage(self):
        for hardware in self.hardware:
            if str(hardware.HardwareType) == 'GpuNvidia':
                for sensor in hardware.Sensors:
                    if str(sensor.Name) == 'GPU Memory Used':
                        hardware.Update()
                        return sensor.Value / 100

    def get_gpu_temp(self):
        for hardware in self.hardware:
            if str(hardware.HardwareType) == 'GpuNvidia':
                for sensor in hardware.Sensors:
                    if str(sensor.SensorType) == 'Temperature':
                        hardware.Update()
                        return sensor.Value

    def get_ram_usage(self):
        for hardware in self.hardware:
            if str(hardware.HardwareType) == 'RAM':
                for sensor in hardware.Sensors:
                    if str(sensor.Name) == 'Used Memory':
                        hardware.Update()
                        return sensor.Value / self.total_ram_memory * 100

if __name__ == '__main__':
    HW = HardWare()
    while True:
        print(f'CPU: {HW.get_cpu_usage()}%')
        print(f'GPU: {HW.get_gpu_temp()}°C')
        print(f'GPU: {HW.get_gpu_usage()}GB')
        print(f'RAM: {HW.get_ram_usage()}%')
