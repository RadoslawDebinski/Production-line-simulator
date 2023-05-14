import sys
from PySide2.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QLabel, QGroupBox, QScrollBar, QFrame
from PySide2.QtUiTools import QUiLoader
import threading
import pythoncom
from hardwareInfo import HardWare
import images.images


class InputUI(QMainWindow):
    def __init__(self):
        super(InputUI, self).__init__()

        # Load the ui file
        loader = QUiLoader()
        self.ui = loader.load("mainUI.ui", self)
        self.ui.setWindowTitle("Information")

        # Find the QGroupBoxes and add charts to them
        gpu_temp_group_box = self.ui.findChild(QGroupBox, "cpuTempGroupBox")
        cpu_use_group_box = self.ui.findChild(QGroupBox, "cpuUseGroupBox")
        gpu_mem_group_box = self.ui.findChild(QGroupBox, "fanGroupBox")
        ram_group_box = self.ui.findChild(QGroupBox, "ramGroupBox")

        # Find the QScrollBars
        gpu_temp_scroll_bar = self.ui.findChild(QScrollBar, "cpuTempVerticalScrollBar")
        cpu_use_scroll_bar = self.ui.findChild(QScrollBar, "cpuUseVerticalScrollBar")
        gpu_mem_scroll_bar = self.ui.findChild(QScrollBar, "fanVerticalScrollBar")
        ram_scroll_bar = self.ui.findChild(QScrollBar, "ramVerticalScrollBar")

        # Find the threshold informing boxes
        self.gpu_temp_button = self.ui.findChild(QPushButton, "tempButton")
        self.cpu_use_button = self.ui.findChild(QPushButton, "useButton")
        self.gpu_mem_button = self.ui.findChild(QPushButton, "fanButton")
        self.ram_button = self.ui.findChild(QPushButton, "ramButton")

        # Create indicators
        self.indicators_scaler = 1.9
        self.gpu_temp_indicator = QFrame(self.ui)
        self.cpu_use_indicator = QFrame(self.ui)
        self.gpu_mem_indicator = QFrame(self.ui)
        self.ram_indicator = QFrame(self.ui)

        # Values
        self.gpu_temp_value = QFrame(gpu_temp_group_box)
        self.gpu_temp_value.move(50, 50)
        self.gpu_temp_value_label = QLabel("")
        self.gpu_temp_value_label.setParent(self.gpu_temp_value)

        self.cpu_use_value = QFrame(cpu_use_group_box)
        self.cpu_use_value.move(50, 50)
        self.cpu_use_value_label = QLabel("")
        self.cpu_use_value_label.setParent(self.cpu_use_value)

        self.gpu_mem_value = QFrame(gpu_mem_group_box)
        self.gpu_mem_value.move(50, 50)
        self.gpu_mem_value_label = QLabel("")
        self.gpu_mem_value_label.setParent(self.gpu_mem_value)

        self.ram_value = QFrame(ram_group_box)
        self.ram_value.move(50, 50)
        self.ram_value_label = QLabel("")
        self.ram_value_label.setParent(self.ram_value)

        # Connect Our Widgets
        gpu_temp_scroll_bar.valueChanged.connect(self.handle_temp_scroll_bar_value_changed)
        cpu_use_scroll_bar.valueChanged.connect(self.handle_use_scroll_bar_value_changed)
        gpu_mem_scroll_bar.valueChanged.connect(self.handle_gpu_mem_scroll_bar_value_changed)
        ram_scroll_bar.valueChanged.connect(self.handle_ram_scroll_bar_value_changed)

        # Set up hardware
        self.HW = HardWare()

        # Set up values for emergency detection
        self.gpu_temp_thresh = 110
        self.cpu_usage_thresh = 110
        self.gpu_usage_thresh = 110
        self.ram_usage_thresh = 110

        values_thread = threading.Thread(target=self.update_values)
        values_thread.start()
        # # Set up background
        # bg_image_path = ":/robotics/parts/arm"
        # bg_image = QPixmap(bg_image_path)
        # self.ui.setStyleSheet(f"background-image: url({bg_image_path})")
        # Show the app
        self.ui.show()

    def handle_temp_scroll_bar_value_changed(self, value):
        self.gpu_temp_thresh = 100 - value
        # Set visible value on button
        self.gpu_temp_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.gpu_temp_indicator.setFixedSize(120, 2)
        self.gpu_temp_indicator.move(50, 40 + value * self.indicators_scaler)
        self.gpu_temp_indicator.setStyleSheet("background-color: red;")

    def handle_use_scroll_bar_value_changed(self, value):
        self.cpu_usage_thresh = 100 - value
        # Set visible value on button
        self.cpu_use_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.cpu_use_indicator.setFixedSize(120, 2)
        self.cpu_use_indicator.move(200, 40 + value * self.indicators_scaler)
        self.cpu_use_indicator.setStyleSheet("background-color: green;")

    def handle_gpu_mem_scroll_bar_value_changed(self, value):
        self.gpu_usage_thresh = 100 - value
        # Set visible value on button
        self.gpu_mem_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.gpu_mem_indicator.setFixedSize(120, 2)
        self.gpu_mem_indicator.move(350, 40 + value * self.indicators_scaler)
        self.gpu_mem_indicator.setStyleSheet("background-color: blue;")

    def handle_ram_scroll_bar_value_changed(self, value):
        self.ram_usage_thresh = 100 - value
        # Set visible value on button
        self.ram_button.setText(f"Threshold: {100 - value}%")
        # Set position, size and color for indicator
        self.ram_indicator.setFixedSize(120, 2)
        self.ram_indicator.move(500, 40 + value * self.indicators_scaler)
        self.ram_indicator.setStyleSheet("background-color: yellow;")

    def update_values(self):
        while True:
            # Get PC parameters
            pythoncom.CoInitialize()
            gpu_temp = self.HW.get_gpu_temp()
            cpu_usage = self.HW.get_cpu_usage()
            gpu_usage = self.HW.get_gpu_usage()
            ram_usage = self.HW.get_ram_usage()
            # Check emergency situations
            self.check_emergency(gpu_temp, cpu_usage, gpu_usage, ram_usage)
            # Set CPU usage
            self.cpu_use_value.setFixedSize(100, cpu_usage * self.indicators_scaler)
            self.cpu_use_value.move(10, 211 - cpu_usage * self.indicators_scaler)  # 230 - cpu_usage * self.indicators_scaler
            self.cpu_use_value.setStyleSheet("background-color: rgb(2, 161, 47);")
            self.cpu_use_value_label.setText(f"{cpu_usage}")
            # Set GPU temp
            self.gpu_temp_value.setFixedSize(100, gpu_temp * self.indicators_scaler)
            self.gpu_temp_value.move(10, 211 - gpu_temp * self.indicators_scaler)
            self.gpu_temp_value.setStyleSheet("background-color: rgb(252, 73, 3);")
            self.gpu_temp_value_label.setText(f"{gpu_temp}")
            # Set GPU usage
            self.gpu_mem_value.setFixedSize(100, gpu_usage * self.indicators_scaler)
            self.gpu_mem_value.move(10, 211 - gpu_usage * self.indicators_scaler)
            self.gpu_mem_value.setStyleSheet("background-color: rgb(5, 128, 181);")
            self.gpu_mem_value_label.setText(f"{gpu_usage}")
            # Set RAM usage
            self.ram_value.setFixedSize(100, ram_usage * self.indicators_scaler)
            self.ram_value.move(10, 211 - ram_usage * self.indicators_scaler)
            self.ram_value.setStyleSheet("background-color: rgb(194, 191, 2);")
            self.ram_value_label.setText(f"{ram_usage}")

    def check_emergency(self, gpu_temp, cpu_usage, gpu_usage, ram_usage):
        self.gpu_temp_button.setStyleSheet(
            "background-color: red;" if gpu_temp > self.gpu_temp_thresh else "background-color: white;")
        self.cpu_use_button.setStyleSheet(
            "background-color: red;" if cpu_usage > self.cpu_usage_thresh else "background-color: white;")
        self.gpu_mem_button.setStyleSheet(
            "background-color: red;" if gpu_usage > self.gpu_usage_thresh else "background-color: white;")
        self.ram_button.setStyleSheet(
            "background-color: red;" if ram_usage > self.ram_usage_thresh else "background-color: white;")



# Initialize the App
if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = InputUI()
    app.exec_()