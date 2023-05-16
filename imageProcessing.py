import cv2
import glob

import numpy as np


class ImageProcessing:
    def __init__(self, path, line_length=550, segment_length=5):
        self.line_length = line_length
        self.segment_length = segment_length
        self.file_names = list(glob.glob(f'{path}\\*'))
        self.images = []
        self.line = []
        self.line_inv = None
        self.get_source_images()
        self.create_images()

        write_path = f'{path}\\img0.jpg'
        cv2.imwrite(write_path, self.line)
        write_path = f'{path}\\img1.jpg'
        cv2.imwrite(write_path, self.line_inv)

    def get_source_images(self):
        self.images = np.array([cv2.imread(file_name) for file_name in self.file_names])

    def create_images(self):
        images_inv = self.images[::-1]
        line = np.array(self.images)
        no_segments = self.line_length / self.segment_length
        for _ in range(int(no_segments/2)-1):
            line = np.concatenate([line, self.images])
        self.line = cv2.hconcat(line)
        self.line_inv = cv2.rotate(self.line, cv2.ROTATE_180)

    def get_images(self):
        return self.line, self.line_inv


if __name__ == '__main__':
    ImageProcessing('.\\lineSourceImages')
