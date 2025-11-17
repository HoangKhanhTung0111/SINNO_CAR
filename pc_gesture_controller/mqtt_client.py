# mqtt_client.py
import paho.mqtt.client as mqtt
from typing import Optional


class MqttPublisher:
    """
    Wrapper đơn giản cho MQTT Publisher dùng paho-mqtt.
    """
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._client: Optional[mqtt.Client] = None

    def connect(self):
        self._client = mqtt.Client()
        # Nếu sau này dùng username/password:
        # self._client.username_pw_set("user", "pass")
        self._client.connect(self._host, self._port, keepalive=60)
        # Chạy loop ở background thread
        self._client.loop_start()

    def publish(self, topic: str, message: str, qos: int = 0, retain: bool = False):
        if self._client is None:
            raise RuntimeError("MQTT client chưa connect. Gọi connect() trước.")
        self._client.publish(topic, message, qos=qos, retain=retain)

    def close(self):
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None
