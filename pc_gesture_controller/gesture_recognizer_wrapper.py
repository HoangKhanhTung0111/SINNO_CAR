# gesture_recognizer_wrapper.py
import time
from typing import Dict, Callable, Optional

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from mqtt_client import MqttPublisher


class GestureRecognizerWrapper:
    """
    Gói Mediapipe Gesture Recognizer (LIVE_STREAM) + logic gửi MQTT.
    """

    def __init__(
        self,
        model_path: str,
        gesture_to_command: Dict[str, str],
        mqtt_publisher: MqttPublisher,
        mqtt_topic: str,
        min_command_interval_sec: float = 0.7,
    ):
        self._gesture_to_command = gesture_to_command
        self._publisher = mqtt_publisher
        self._topic = mqtt_topic
        self._min_interval = min_command_interval_sec

        self._last_command: Optional[str] = None
        self._last_send_time = 0.0

        self._mp_image_format = mp.ImageFormat.SRGB

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
        )

        self._recognizer = vision.GestureRecognizer.create_from_options(options)

    # Callback được Mediapipe gọi mỗi khi có kết quả
    def _result_callback(
        self,
        result: vision.GestureRecognizerResult,
        output_image: mp.Image,
        timestamp_ms: int,
    ):
        if not result.gestures:
            return

        # gestures[0] là list các candidate, lấy cái có score cao nhất
        top_gesture = result.gestures[0][0]
        label = top_gesture.category_name
        score = top_gesture.score

        if label not in self._gesture_to_command:
            # Gesture không được dùng -> bỏ qua
            return

        command = self._gesture_to_command[label]
        now = time.time()

        # Gửi nếu:
        # - khác command trước, hoặc
        # - đã qua đủ thời gian min_interval
        if command != self._last_command or (now - self._last_send_time) > self._min_interval:
            self._publisher.publish(self._topic, command)
            print(f"[GESTURE] {label} (score={score:.2f}) -> MQTT '{command}'")
            self._last_command = command
            self._last_send_time = now

    def process_frame(self, frame_bgr, timestamp_ms: int):
        """
        Nhận một frame BGR (OpenCV), convert sang RGB, tạo mp.Image và gọi recognize_async.
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=self._mp_image_format, data=frame_rgb)
        self._recognizer.recognize_async(mp_image, timestamp_ms)

    def close(self):
        self._recognizer.close()
