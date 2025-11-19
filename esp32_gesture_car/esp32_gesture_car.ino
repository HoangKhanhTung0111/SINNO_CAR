// esp32_gesture_car.ino

#include <WiFi.h>
#include <PubSubClient.h>

#include "config.h"
#include "motor_driver.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// --- Wi-Fi ---
const char* WIFI_SSID     = ".";
const char* WIFI_PASSWORD = "Hoangtung111";

// --- MQTT ---
const char* MQTT_SERVER   = "172.20.10.4";  // IP máy chạy Docker EMQX
const char* MQTT_CLIENT_ID = "ESP32_Gesture_Car";
const char* MQTT_TOPIC_SUB = "/aiot/gesture";

// --- Hàm xử lý khi nhận MQTT message ---
// esp32_gesture_car.ino (đoạn callback)
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }

    Serial.print("[MQTT] Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    Serial.println(message);

    if (message == "FORWARD") {
        Serial.println("[ACTION] FORWARD");
        motor_forward();
    } else if (message == "LEFT") {
        Serial.println("[ACTION] LEFT");
        motor_left();
    } else if (message == "RIGHT") {
        Serial.println("[ACTION] RIGHT");
        motor_right();
    } else {
        Serial.println("[ACTION] UNKNOWN COMMAND → motor_stop()");
        motor_stop();
    }
}

// --- Kết nối Wi-Fi ---
void setup_wifi() {
    Serial.print("Connecting to Wi-Fi: ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("Wi-Fi connected.");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

// --- Kết nối lại MQTT nếu mất --- 
void reconnect_mqtt() {
    while (!mqttClient.connected()) {
        Serial.print("Connecting to MQTT...");
        if (mqttClient.connect(MQTT_CLIENT_ID)) {
            Serial.println("connected.");
            mqttClient.subscribe(MQTT_TOPIC_SUB);
            Serial.print("Subscribed to topic: ");
            Serial.println(MQTT_TOPIC_SUB);
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println("  try again in 2 seconds");
            delay(2000);
        }
    }
}

void setup() {
    Serial.begin(115200);

    motor_driver_init();
    setup_wifi();

    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);

    reconnect_mqtt();
}

void loop() {
    if (!mqttClient.connected()) {
        reconnect_mqtt();
    }
    mqttClient.loop();

    // Nếu muốn, có thể thêm logic timeout ở đây:
    // VD: nếu 3 giây không có lệnh mới -> motor_stop().
}
