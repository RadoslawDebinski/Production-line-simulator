import sys
import time
from PySide2.QtCore import Qt, QFile, QTimer, QObject, QThread, Signal, Slot, QCoreApplication
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QLabel, QGroupBox, QScrollBar, QFrame, QVBoxLayout
from PySide2.QtCharts import QtCharts
from PySide2.QtUiTools import QUiLoader
import psutil
import wmi


class Worker(QObject):
    update_signal = Signal(int)

    def __init__(self):
        super().__init__()

    def update(self):
        while True:
            # Emit the signal with the updated value
            self.update_signal.emit(0)
            QCoreApplication.processEvents()
            time.sleep(0.25)

class InputUI(QMainWindow):
    def __init__(self, chart_view=None):
        super(InputUI, self).__init__()

        # Load the ui file
        loader = QUiLoader()
        self.ui = loader.load("mainUI.ui", self)
        self.ui.setWindowTitle("Information")

        # Find the QGroupBoxes and add charts to them
        cpu_temp_group_box = self.ui.findChild(QGroupBox, "cpuTempGroupBox")
        self.chart1View = QtCharts.QChartView()
        self.chart1View.setMinimumHeight(190)
        self.chart1Layout = QVBoxLayout()
        self.chart1Layout.addWidget(self.chart1View)
        cpu_temp_group_box.setLayout(self.chart1Layout)

        # Create a QChart instance
        chart1 = QtCharts.QChart()
        chart1.setTitle("My Bar Chart")

        # Create a QBarSeries instance and add it to the chart
        self.series1 = QtCharts.QBarSeries()
        chart1.addSeries(self.series1)

        # Customize the chart
        chart1.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart1.setTheme(QtCharts.QChart.ChartThemeBlueCerulean)
        chart1.legend().hide()

        # Set the chart to be displayed in the QChartView
        self.chart1View.setChart(chart1)

        cpu_use_group_box = self.ui.findChild(QGroupBox, "cpuUseGroupBox")
        self.chart2View = QtCharts.QChartView()
        self.chart2View.setMinimumHeight(190)
        self.chart2Layout = QVBoxLayout()
        self.chart2Layout.addWidget(self.chart2View)
        cpu_use_group_box.setLayout(self.chart2Layout)

        fan_group_box = self.ui.findChild(QGroupBox, "fanGroupBox")
        self.chart3View = QtCharts.QChartView()
        self.chart3View.setMinimumHeight(190)
        self.chart3Layout = QVBoxLayout()
        self.chart3Layout.addWidget(self.chart3View)
        fan_group_box.setLayout(self.chart3Layout)

        ram_group_box = self.ui.findChild(QGroupBox, "ramGroupBox")
        self.chart4View = QtCharts.QChartView()
        self.chart4View.setMinimumHeight(190)
        self.chart4Layout = QVBoxLayout()
        self.chart4Layout.addWidget(self.chart4View)
        ram_group_box.setLayout(self.chart4Layout)

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

        # Connect Our Widgets
        cpu_temp_scroll_bar.valueChanged.connect(self.handle_temp_scroll_bar_value_changed)
        cpu_use_scroll_bar.valueChanged.connect(self.handle_use_scroll_bar_value_changed)
        fan_scroll_bar.valueChanged.connect(self.handle_fan_scroll_bar_value_changed)
        ram_scroll_bar.valueChanged.connect(self.handle_ram_scroll_bar_value_changed)

        # Create the worker and thread
        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # Connect signals/slots
        self.worker.update_signal.connect(self.update_values)
        self.worker_thread.started.connect(self.worker.update)

        # Start the thread
        self.worker_thread.start()

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
        print(cpu_usage)
        # fan_speed = self.get_fan_speed()
        # ram_usage = self.get_ram_usage()

        # Create a QBarSet instance with the value you want to display and add it to the QBarSeries
        # Clear the old data
        self.series1.clear()

        # Add the new data
        set1 = QtCharts.QBarSet("Data")
        set1.append(20)
        self.series1.append(set1)

        # Update the chart
        self.chart1View.chart().update()



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
