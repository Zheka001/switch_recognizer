# -*- coding: utf-8 -*-
import cv2
import numpy as np
import random
from time import monotonic as now

from src.utils.config import SingleConfig


class VideoProcessor:
    """
        Класс, предназначенный для обработки видео с целью определения положения элегазового выключателя.
    """
    def __init__(self):
        self._answers = list()
        self._cap = None

        config = SingleConfig().video_processor
        self._min_circle_radius = config.min_circle_radius
        self._max_circle_radius = config.max_circle_radius
        self._min_hue = config.min_color_hue
        self._max_hue = config.max_color_hue
        self._min_area = config.min_area
        self._frames_per_second = config.frames_per_second

    def run(self, filename):
        start_time = now()
        self._answers = list()

        self._cap = cv2.VideoCapture(str(filename))
        fps = round(self._cap.get(cv2.CAP_PROP_FPS))
        duration = round(round(self._cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps)
        frame_counter = 0
        need_to_decode_counter = 0

        self._frames_per_second = min(fps, self._frames_per_second)
        sample = random.sample(range(fps), self._frames_per_second)
        while True:
            sample = random.sample(range(fps), self._frames_per_second) if need_to_decode_counter == 0 else sample
            ret, frame = self._process_capture(need_to_decode=need_to_decode_counter in sample)
            if not ret:
                break
            frame_counter += 1
            need_to_decode_counter = (need_to_decode_counter + 1) % fps
            if frame is None:
                continue
            self.process_image(frame)
        self._cap.release()

        exec_time = round(now() - start_time, 2)
        return self._analyze_answers(exec_time, filename, duration)

    def process_image(self, image):
        self._find_circles(image)

    def _analyze_answers(self, exec_time, filename, duration):
        if len(self._answers) == 0:
            return {
                'status_of_switcher': None,
                'confidence': None,
                'processed_frames': len(self._answers),
                'video_duration': duration,
                'time_execution': exec_time,
                'url': str(filename)
            }

        turn_on = len([a for a in self._answers if a])
        turn_off = len([a for a in self._answers if not a])
        status = int(turn_on > turn_off)
        right_answers = turn_on if status else turn_off
        confidence = round(right_answers / len(self._answers), 2)
        return {
            'status_of_switcher': status,
            'confidence': confidence,
            'processed_frames': len(self._answers),
            'video_duration': duration,
            'time_execution': exec_time,
            'url': str(filename)
        }

    def _find_circles(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=150, param2=60,
                                   minRadius=self._min_circle_radius, maxRadius=self._max_circle_radius)

        if circles is not None:
            circles = np.around(circles).astype(np.int)
            for p in circles[0, :]:
                r_min, r_max = p[1] - p[2], p[1] + p[2]
                c_min, c_max = p[0] - p[2], p[0] + p[2]
                rect = image[r_min:r_max, c_min:c_max, :]
                if min(rect.shape) == 0:
                    continue
                status = self._check_for_orange(rect)
                if status is not None:
                    self._answers.append(status)

    def _check_for_orange(self, image):
        hsv_min = np.array((self._min_hue, 100, 80), np.uint8)
        hsv_max = np.array((self._max_hue, 255, 255), np.uint8)

        # преобразуем RGB картинку в HSV модель
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # применяем цветовой фильтр
        mask = cv2.inRange(hsv, hsv_min, hsv_max)

        # вычисляем моменты изображения
        moments = cv2.moments(mask, 1)
        # m01 = moments['m01']
        m10 = moments['m10']
        area = moments['m00']

        if area > self._min_area:
            x = int(m10 / area)
            # y = int(m01 / area)
            # print(area, x, y, image.shape[:2], x < image.shape[1] // 2)
            # cv2.imshow('rect', image)
            # cv2.imshow('mask', mask)
            # cv2.waitKey(0)
            return x < image.shape[1] // 2

        return None

    def _process_capture(self, need_to_decode=True):
        ret, image = self._cap.read() if need_to_decode else (self._cap.grab(), None)
        return ret, image


if __name__ == '__main__':
    vp = VideoProcessor()
    from pathlib import Path
    # for video in Path('data').rglob('*.MOV'):
    #     if '39' in str(video):
    #         vp.run(video)
    for video in Path('data').rglob('*.MOV'):
        result = vp.run(video)
        print(result)
