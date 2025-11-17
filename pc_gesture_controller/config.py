# config.py

# --- MQTT ---
MQTT_BROKER_HOST = "localhost"   # máy chạy Docker EMQX
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_GESTURE = "/aiot/gesture"

# --- Gesture mapping ---
# Mediapipe label -> command string gửi qua MQTT
GESTURE_TO_COMMAND = {
    "Closed_Fist": "LEFT",     # rẽ trái
    "Open_Palm": "RIGHT",      # rẽ phải
    "Pointing_Up": "FORWARD",  # đi thẳng
}

# Thời gian tối thiểu giữa 2 lần gửi cùng một command (giảm spam)
MIN_COMMAND_INTERVAL_SEC = 0.7

# Đường dẫn model
MODEL_PATH = "models/gesture_recognizer.task"

# Thiết bị camera (0: webcam mặc định)
CAMERA_INDEX = 0
