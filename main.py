import sys
import psutil
from PySide2.QtCore import Qt, QFile, QTimer
from PySide2.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QLabel, QGroupBox, QScrollBar, QFrame, QVBoxLayout
from PySide2.QtCharts import QtCharts
from PySide2.QtUiTools import QUiLoader
import wmi


class InputUI(QMainWindow):
    def __init__(self):
        super(InputUI, self).__init__()

        # Load the ui file
        loader = QUiLoader()
        self.ui = loader.load("mainUI.ui", self)
        self.ui.setWindowTitle("Information")

        # Find the QGroupBoxes and add charts to them
        cpu_temp_group_box = self.ui.findChild(QGroupBox, "cpuTempGroupBox")
        cpu_use_group_box = self.ui.findChild(QGroupBox, "cpuUseGroupBox")
        fan_group_box = self.ui.findChild(QGroupBox, "fanGroupBox")
        ram_group_box = self.ui.findChild(QGroupBox, "ramGroupBox")

        # Find the QScrollBars
        cpu_temp_scroll_bar = self.ui.findChild(QScrollBar, "cpuTempVerticalScrollBar")
        cpu_use_scroll_bar = self.ui.findChild(QScrollBar, "cpuUseVerticalScrollBar")
        fan_scroll_bar = self.ui.findChild(QScrollBar, "fanVerticalScrollBar")
        ram_scroll_bar = self.ui.findChild(QScrollBar, "ramVerticalScrollBar")

        # Find the threshold informing boxes
        self.cpu_temp_button = self.ui.findChild(QPushButton, "tempButton")
        self.cpu_use_button = self.ui.findChild(QPushButton, "useButton")
        self.fan_button = self.ui.findChild(QPushButton, "fanButton")
        self.ram_button = self.ui.findChild(QPushButton, "ramButton")

        # Create indicators
        self.indicators_scaler = 1.9
        self.cpu_temp_indicator = QFrame(self.ui)
        self.cpu_use_indicator = QFrame(self.ui)
        self.fan_indicator = QFrame(self.ui)
        self.ram_indicator = QFrame(self.ui)

        # Values
        self.cpu_temp_value = QFrame(self.ui)
        self.cpu_temp_value_label = QLabel("#####")
        self.cpu_temp_value_label.setParent(self.cpu_temp_value)

        self.cpu_use_value = QFrame(self.ui)
        self.cpu_use_value_label = QLabel("#####")
        self.cpu_use_value_label.setParent(self.cpu_use_value)

        self.fan_value = QFrame(self.ui)
        self.fan_value_label = QLabel("#####")
        self.fan_value_label.setParent(self.fan_value)

        self.ram_value = QFrame(self.ui)
        self.ram_value_label = QLabel("#####")
        self.ram_value_label.setParent(self.ram_value)

        # Set up the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_values)
        self.timer.start(250)  # Update every 0.25 seconds

        # Connect Our Widgets
        cpu_temp_scroll_bar.valueChanged.connect(self.handle_temp_scroll_bar_value_changed)
        cpu_use_scroll_bar.valueChanged.connect(self.handle_use_scroll_bar_value_changed)
        fan_scroll_bar.valueChanged.connect(self.handle_fan_scroll_bar_value_changed)
        ram_scroll_bar.valueChanged.connect(self.handle_ram_scroll_bar_value_changed)
        # Show the app
        self.ui.show()

    def handle_temp_scroll_bar_value_changed(self, value):
        print("Scroll bar position:", value)
        # Set visible value on button
        self.cpu_temp_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.cpu_temp_indicator.setFixedSize(120, 2)
        self.cpu_temp_indicator.move(50, 40 + value * self.indicators_scaler)
        self.cpu_temp_indicator.setStyleSheet("background-color: red;")

    def handle_use_scroll_bar_value_changed(self, value):
        print("Scroll bar position:", value)
        # Set visible value on button
        self.cpu_use_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.cpu_use_indicator.setFixedSize(120, 2)
        self.cpu_use_indicator.move(200, 40 + value * self.indicators_scaler)
        self.cpu_use_indicator.setStyleSheet("background-color: red;")

    def handle_fan_scroll_bar_value_changed(self, value):
        print("Scroll bar position:", value)
        # Set visible value on button
        self.fan_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.fan_indicator.setFixedSize(120, 2)
        self.fan_indicator.move(350, 40 + value * self.indicators_scaler)
        self.fan_indicator.setStyleSheet("background-color: red;")

    def handle_ram_scroll_bar_value_changed(self, value):
        print("Scroll bar position:", value)
        # Set visible value on button
        self.ram_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.ram_indicator.setFixedSize(120, 2)
        self.ram_indicator.move(500, 40 + value * self.indicators_scaler)
        self.ram_indicator.setStyleSheet("background-color: red;")

    def update_values(self):
        # Get PC parameters
        # cpu_temp = self.get_cpu_temp()
        cpu_usage = self.get_cpu_usage()
        # fan_speed = self.get_fan_speed()
        # ram_usage = self.get_ram_usage()

        # Get CPU usage
        self.cpu_use_value.setFixedSize(100, cpu_usage * self.indicators_scaler)
        self.cpu_use_value.move(60, 230 - cpu_usage * self.indicators_scaler)
        self.cpu_use_value.setStyleSheet("background-color: red;")
        self.cpu_use_value_label.setText(f"{cpu_usage}")

    def get_cpu_temp(self):
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor", find_classes=True)
        temperature_infos = w.Sensor()
        cpu_temps = [x for x in temperature_infos if x.SensorType == u'Temperature' and x.Name == u'CPU Core']
        return float(cpu_temps[0].Value) if float(cpu_temps[0].Value) is not None else 0

    def get_cpu_usage(self):
        w = wmi.WMI(namespace="root\cimv2")
        cpu_load = w.Win32_Processor()[0].LoadPercentage
        return cpu_load if cpu_load is not None else 0

    def get_fan_speed(self):
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        sensor_infos = w.Sensor()
        fan_speeds = [x for x in sensor_infos if x.SensorType == u'Fan' and x.Name.startswith('CPU')]
        return fan_speeds[0].Value if fan_speeds[0].Value is not None else 0

    def get_ram_usage(self):
        w = wmi.WMI(namespace="root\cimv2")
        ram_usage = w.Win32_OperatingSystem()[0].FreePhysicalMemory / w.Win32_ComputerSystem()[0].TotalPhysicalMemory \
                    * 100
        return ram_usage if ram_usage is not None else 0


# Initialize the App
if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = InputUI()
    app.exec_()
