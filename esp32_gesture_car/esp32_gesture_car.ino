// esp32_gesture_car.ino

#include <WiFi.h>
#include <PubSubClient.h>

#include "config.h"
#include "motor_driver.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// --- Wi-Fi ---
const char* WIFI_SSID     = "Hust_B1_Staff";
const char* WIFI_PASSWORD = "";

// --- MQTT ---
const char* MQTT_SERVER   = "172.11.108.190";  // IP máy chạy Docker EMQX
const char* MQTT_CLIENT_ID = "ESP32_Gesture_Car";
const char* MQTT_TOPIC_SUB = "/aiot/gesture";

unsigned long lastCommandMillis = 0;
bool motorsStopped = true;  

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

    // Cập nhật thời gian nhận lệnh cuối cùng
    lastCommandMillis = millis();

    if (message == "FORWARD") {
        Serial.println("[ACTION] FORWARD");
        motor_forward();
        motorsStopped = false;
    } else if (message == "LEFT") {
        Serial.println("[ACTION] LEFT");
        motor_left();
        motorsStopped = false;
    } else if (message == "RIGHT") {
        Serial.println("[ACTION] RIGHT");
        motor_right();
        motorsStopped = false;
    } else if (message == "STOP") {
        Serial.println("[ACTION] STOP");
        motor_stop();
        motorsStopped = true;
    } else {
        Serial.println("[ACTION] UNKNOWN COMMAND → motor_stop()");
        motor_stop();
        motorsStopped = true;
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
    delay(1000);
    Serial.println("\n[SETUP] ESP32 Gesture Car starting...");

    motor_driver_init();
    motor_stop();
    motorsStopped = true;
    lastCommandMillis = millis();

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

    // ===== Timeout 3 giây không có lệnh thì dừng motor =====
    unsigned long now = millis();
    const unsigned long TIMEOUT_MS = 3000;  // 3 giây

    if (!motorsStopped && (now - lastCommandMillis > TIMEOUT_MS)) {
        Serial.println("[TIMEOUT] No command for 3s → STOP motors");
        motor_stop();
        motorsStopped = true;
    }

    // ... nếu bạn không có logic gì thêm thì để loop trống ở đây
}
