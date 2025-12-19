# main.py
import cv2

from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC_GESTURE,
    GESTURE_TO_COMMAND,
    MODEL_PATH,
    MIN_COMMAND_INTERVAL_SEC,
    CAMERA_INDEX,
    STOP_COMMAND,          # <-- thêm dòng này
)
from mqtt_client import MqttPublisher
from gesture_recognizer_wrapper import GestureRecognizerWrapper


def main():
    mqtt = MqttPublisher(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    mqtt.connect()
    print(f"[INFO] Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

    recognizer = GestureRecognizerWrapper(
        model_path=MODEL_PATH,
        gesture_to_command=GESTURE_TO_COMMAND,
        mqtt_publisher=mqtt,
        mqtt_topic=MQTT_TOPIC_GESTURE,
        min_command_interval_sec=MIN_COMMAND_INTERVAL_SEC,
        stop_command=STOP_COMMAND,   # <-- truyền STOP vào đây
    )

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[ERROR] Không mở được webcam.")
        return

    print("[INFO] Nhấn 'q' để thoát.")

    timestamp_ms = 0
    FRAME_INTERVAL_MS = 33  # ~30fps

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Không đọc được frame từ camera.")
                break

            timestamp_ms += FRAME_INTERVAL_MS
            recognizer.process_frame(frame, timestamp_ms)

            cv2.imshow("Gesture Control (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        recognizer.close()
        mqtt.close()
        print("[INFO] Đã dừng chương trình.")


if __name__ == "__main__":
    main()
