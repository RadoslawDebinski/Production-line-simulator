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