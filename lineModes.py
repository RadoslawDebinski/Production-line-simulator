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