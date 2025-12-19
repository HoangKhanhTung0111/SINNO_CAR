# gesture_recognizer_wrapper.py
import time
from typing import Dict, Optional

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from mqtt_client import MqttPublisher


class GestureRecognizerWrapper:
    """
    Mediapipe Gesture Recognizer (LIVE_STREAM) + logic gửi MQTT.
    - 3 gesture điều khiển: Closed_Fist, Open_Palm, Pointing_Up
    - Gesture khác → gửi STOP, nhưng có "grace period" để tránh stop quá sớm.
    """

    def __init__(
        self,
        model_path: str,
        gesture_to_command: Dict[str, str],
        mqtt_publisher: MqttPublisher,
        mqtt_topic: str,
        min_command_interval_sec: float = 0.7,
        stop_command: str = "STOP",
        stop_grace_sec: float = 0.7,   # thời gian tối thiểu cho xe chạy trước khi cho STOP xen vào
    ):
        self._gesture_to_command = gesture_to_command
        self._stop_command = stop_command
        self._publisher = mqtt_publisher
        self._topic = mqtt_topic
        self._min_interval = min_command_interval_sec
        self._stop_grace_sec = stop_grace_sec

        self._last_command: Optional[str] = None
        self._last_send_time = 0.0       # lần publish bất kỳ command gần nhất
        self._last_motion_time = 0.0     # lần publish LEFT/RIGHT/FORWARD gần nhất

        self._mp_image_format = mp.ImageFormat.SRGB

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
        )

        self._recognizer = vision.GestureRecognizer.create_from_options(options)
        self._debug_counter = 0

    def _result_callback(
        self,
        result: vision.GestureRecognizerResult,
        output_image: mp.Image,
        timestamp_ms: int,
    ):
        self._debug_counter += 1

        num_gestures = len(result.gestures) if result.gestures is not None else 0
        num_hands = len(result.hand_landmarks) if result.hand_landmarks is not None else 0

        if self._debug_counter % 10 == 0:
            print(
                f"[DEBUG] Callback #{self._debug_counter} at {timestamp_ms} ms - "
                f"hands={num_hands}, gestures={num_gestures}"
            )

        # Không có gesture → coi như không có lệnh mới, để ESP32 tự timeout 3s
        if not result.gestures or num_gestures == 0:
            if self._debug_counter % 30 == 0:
                print("[DEBUG] No gesture detected (no recognized hand pose).")
            return

        # Lấy list candidate cho bàn tay đầu tiên
        candidates = result.gestures[0]

        # In bớt cho dễ debug (mỗi lần)
        print("[DEBUG] Candidates:")
        for cand in candidates:
            print(f"    - label='{cand.category_name}', score={cand.score:.3f}")

        # Lấy candidate có score cao nhất
        top_gesture = max(candidates, key=lambda c: c.score)
        label = top_gesture.category_name
        score = top_gesture.score

        MIN_SCORE = 0.5
        now = time.time()

        # ============================
        # 1) Gesture thuộc 3 nhãn điều khiển
        # ============================
        if label in self._gesture_to_command and score >= MIN_SCORE:
            command = self._gesture_to_command[label]

            # Điều kiện gửi lệnh điều khiển:
            should_send = (
                command != self._last_command
                or (now - self._last_send_time) > self._min_interval
            )

            if should_send:
                self._publisher.publish(self._topic, command)
                print(f"[GESTURE] {label} (score={score:.2f}) -> MQTT '{command}'")
                self._last_command = command
                self._last_send_time = now
                self._last_motion_time = now   # cập nhật thời điểm "đã cho xe chạy"

            return

        # ============================
        # 2) Gesture KHÔNG thuộc 3 nhãn → ứng viên STOP
        # ============================

        # Nếu mới vừa chạy lệnh điều khiển gần đây (< stop_grace_sec)
        # thì bỏ qua STOP để tránh vừa LEFT/RIGHT/FORWARD xong đã STOP ngay.
        time_since_motion = now - self._last_motion_time
        if time_since_motion < self._stop_grace_sec:
            print(
                f"[DEBUG] Gesture '{label}' (score={score:.2f}) not in mapping "
                f"BUT in grace period ({time_since_motion:.2f}s < {self._stop_grace_sec}s) → ignore STOP"
            )
            return

        # Hết grace period → cho phép STOP
        if not self._stop_command:
            # nếu dev tắt STOP_COMMAND
            print(
                f"[DEBUG] Gesture '{label}' (score={score:.2f}) not in mapping, "
                f"no STOP_COMMAND configured."
            )
            return

        command = self._stop_command

        # Điều kiện gửi STOP:
        should_send_stop = (
            command != self._last_command
            or (now - self._last_send_time) > self._min_interval
        )

        if should_send_stop:
            self._publisher.publish(self._topic, command)
            print(f"[GESTURE] send STOP due to gesture '{label}' "
                  f"(no motion for {time_since_motion:.2f}s)")
            self._last_command = command
            self._last_send_time = now

    def process_frame(self, frame_bgr, timestamp_ms: int):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=self._mp_image_format, data=frame_rgb)
        self._recognizer.recognize_async(mp_image, timestamp_ms)

    def close(self):
        self._recognizer.close()
