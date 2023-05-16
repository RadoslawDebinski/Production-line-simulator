import sys
import time

import numpy as np
from PySide2.QtCore import QTimer
from PySide2.QtGui import QPixmap, QBrush, QColor
from PySide2.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QLabel, QGroupBox, QScrollBar, QFrame, QVBoxLayout, QRadioButton, QGraphicsScene, QGraphicsView, \
    QGraphicsRectItem
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PySide2.QtUiTools import QUiLoader
import threading
import pythoncom
from hardwareInfo import HardWare
from imageProcessing import ImageProcessing
import images.images


class InputUI(QMainWindow):
    def __init__(self):
        super(InputUI, self).__init__()

        # Load the ui file
        loader = QUiLoader()
        self.ui = loader.load("mainUI.ui", self)
        self.ui.setWindowTitle("Information")

        # Find the QGroupBoxes and add charts to them
        self.gpu_temp_group_box = self.ui.findChild(QGroupBox, "cpuTempGroupBox")
        self.cpu_use_group_box = self.ui.findChild(QGroupBox, "cpuUseGroupBox")
        self.gpu_mem_group_box = self.ui.findChild(QGroupBox, "fanGroupBox")
        self.ram_group_box = self.ui.findChild(QGroupBox, "ramGroupBox")
        self.prod_line_box = self.ui.findChild(QGroupBox, "prodLineGroupBox")

        # Scene for production line
        self.scene = QGraphicsScene(self.prod_line_box)
        self.view = QGraphicsView(self.scene, self.prod_line_box)

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
        self.gpu_temp_value = QFrame(self.gpu_temp_group_box)
        self.gpu_temp_value.move(50, 50)
        self.gpu_temp_value.setStyleSheet("background-color: rgb(252, 73, 3);")
        self.gpu_temp_value_label = QLabel("")
        self.gpu_temp_value_label.setParent(self.gpu_temp_value)

        self.cpu_use_value = QFrame(self.cpu_use_group_box)
        self.cpu_use_value.move(50, 50)
        self.cpu_use_value.setStyleSheet("background-color: rgb(2, 161, 47);")
        self.cpu_use_value_label = QLabel("")
        self.cpu_use_value_label.setParent(self.cpu_use_value)

        self.gpu_mem_value = QFrame(self.gpu_mem_group_box)
        self.gpu_mem_value.move(50, 50)
        self.gpu_mem_value_label = QLabel("")
        self.gpu_mem_value.setStyleSheet("background-color: rgb(5, 128, 181);")
        self.gpu_mem_value_label.setParent(self.gpu_mem_value)

        self.ram_value = QFrame(self.ram_group_box)
        self.ram_value.move(50, 50)
        self.ram_value.setStyleSheet("background-color: rgb(194, 191, 2);")
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
        # Values update thread
        values_thread = threading.Thread(target=self.update_values)
        values_thread.start()
        # Getting line images
        self.pixmap_line = QPixmap(".\\lineSourceImages\\img0.jpg")
        self.pixmap_line_inv = QPixmap(".\\lineSourceImages\\img1.jpg")
        self.line_label = QLabel()
        # Animation frame definition
        self.line_frame_time = 1
        # Line speed controller connection
        self.line_fast_button = self.findChild(QRadioButton, "radioButton")
        self.line_normal_button = self.findChild(QRadioButton, "radioButton_2")
        self.line_slow_button = self.findChild(QRadioButton, "radioButton_3")
        self.line_fast_button.toggled.connect(self.line_speed_fast)
        self.line_normal_button.toggled.connect(self.line_speed_normal)
        self.line_slow_button.toggled.connect(self.line_speed_slow)
        # Line movement thread
        self.frame = True
        self.line_layout = QVBoxLayout()
        self.line_timer = QTimer()
        self.line_timer.timeout.connect(self.line_movement)
        self.line_timer.start(self.line_frame_time * 1000)  # Convert to milliseconds
        # Line boxes
        self.line_no_boxes = 1
        self.boxes_on_line = []
        # Line boxes layout and generation
        self.generate_boxes()
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
            gpu_temp = self.HW.get_gpu_temp() if self.HW.get_gpu_temp() is not None else 0
            cpu_usage = self.HW.get_cpu_usage() if self.HW.get_cpu_usage() is not None else 0
            gpu_usage = self.HW.get_gpu_usage() if self.HW.get_gpu_usage() is not None else 0
            ram_usage = self.HW.get_ram_usage() if self.HW.get_ram_usage() is not None else 0

            gpu_temp = min(
                gpu_temp + self.line_no_boxes * 10 / self.line_frame_time, 100
            )
            cpu_usage = min(
                cpu_usage + self.line_no_boxes * 10 / self.line_frame_time, 100
            )
            gpu_usage = min(
                gpu_usage + self.line_no_boxes * 10 / self.line_frame_time, 100
            )
            ram_usage = min(
                ram_usage + self.line_no_boxes * 10 / self.line_frame_time, 100
            )

            # print(f"gpu_temp:{gpu_temp}, cpu_use:{cpu_usage}, gpu_use:{gpu_usage}, ram_use:{ram_usage}")
            # Check emergency situations
            self.check_emergency(gpu_temp, cpu_usage, gpu_usage, ram_usage)
            # Set CPU usage
            self.cpu_use_value.setFixedSize(100, cpu_usage * self.indicators_scaler)
            self.cpu_use_value.move(10, 211 - cpu_usage * self.indicators_scaler)
            self.cpu_use_value_label.setText(f"{cpu_usage}")
            # Set GPU temp
            self.gpu_temp_value.setFixedSize(100, gpu_temp * self.indicators_scaler)
            self.gpu_temp_value.move(10, 211 - gpu_temp * self.indicators_scaler)
            self.gpu_temp_value_label.setText(f"{gpu_temp}")
            # Set GPU usage
            self.gpu_mem_value.setFixedSize(100, gpu_usage * self.indicators_scaler)
            self.gpu_mem_value.move(10, 211 - gpu_usage * self.indicators_scaler)
            self.gpu_mem_value_label.setText(f"{gpu_usage}")
            # Set RAM usage
            self.ram_value.setFixedSize(100, ram_usage * self.indicators_scaler)
            self.ram_value.move(10, 211 - ram_usage * self.indicators_scaler)
            self.ram_value_label.setText(f"{ram_usage}")
            self.gpu_temp_group_box.update()
            self.cpu_use_group_box.update()
            self.gpu_mem_group_box.update()
            self.ram_group_box.update()
            time.sleep(2)

    def line_speed_fast(self):
        if self.line_fast_button.isChecked():
            self.line_frame_time = 0.5
            self.line_timer.stop()
            self.line_timer.start(self.line_frame_time * 1000)

    def line_speed_normal(self):
        if self.line_normal_button.isChecked():
            self.line_frame_time = 1
            self.line_timer.stop()
            self.line_timer.start(self.line_frame_time * 1000)

    def line_speed_slow(self):
        if self.line_slow_button.isChecked():
            self.line_frame_time = 2
            self.line_timer.stop()
            self.line_timer.start(self.line_frame_time * 1000)

    def generate_boxes(self):
        self.line_no_boxes = np.random.randint(1, 4)
        self.scene = QGraphicsScene(self.prod_line_box)  # Create a QGraphicsScene
        self.view = QGraphicsView(self.scene, self.prod_line_box)  # Create a QGraphicsView and set the scene

        # Add the pixmap to the scene
        self.pixmap_item = self.scene.addPixmap(self.pixmap_line)

        layout = QVBoxLayout()  # Create a layout for self.prod_line_box

        for i in range(self.line_no_boxes):
            box = QGraphicsRectItem(0, 0, 30, 10)
            box.setBrush(QBrush(QColor(115, 59, 10)))  # Set the background color
            self.scene.addItem(box)  # Add the box to the scene

            # Position the box on top of the pixmap
            box.setPos(0, 10 + i * 50)

            self.boxes_on_line.append(box)

        layout.addWidget(self.view)  # Add the QGraphicsView to the layout

        # Set the layout for self.prod_line_box
        self.prod_line_box.setLayout(layout)

    def regenerate_boxes(self):
        for box in self.boxes_on_line:
            self.scene.removeItem(box)
            self.boxes_on_line.remove(box)

        print(len(self.boxes_on_line))

        self.line_no_boxes = np.random.randint(1, 4)
        for i in range(self.line_no_boxes):
            box = QGraphicsRectItem(0, 0, 30, 10)
            box.setBrush(QBrush(QColor(115, 59, 10)))  # Set the background color
            self.scene.addItem(box)  # Add the box to the scene
            # Position the box on top of the pixmap
            box.setPos(0, 10 + i * 50)
            self.boxes_on_line.append(box)

        print(len(self.boxes_on_line))

    def line_movement(self):
        if self.frame:
            self.pixmap_item.setPixmap(self.pixmap_line)
            self.frame = False
        else:
            self.pixmap_item.setPixmap(self.pixmap_line_inv)
            self.frame = True

        border = 490
        for box in self.boxes_on_line:
            box_position = box.pos()
            x, y = box_position.x(), box_position.y()
            if x >= border:
                self.regenerate_boxes()
                break
            box.setPos(x + 10/self.line_frame_time, y)

        print(self.boxes_on_line[0].pos().x())

        self.prod_line_box.update()

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
