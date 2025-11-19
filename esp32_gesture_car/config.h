// config.h
#pragma once

// --- Wi-Fi ---
extern const char* WIFI_SSID;
extern const char* WIFI_PASSWORD;

// --- MQTT ---
extern const char* MQTT_SERVER;  // IP máy chạy Docker EMQX
const int MQTT_PORT     = 1883;
extern const char* MQTT_CLIENT_ID;
extern const char* MQTT_TOPIC_SUB;

// --- TB6612 Motor Pins ---
// Motor A
const int PIN_PWMA = 33;
const int PIN_AIN1 = 26;
const int PIN_AIN2 = 25;

// Motor B
const int PIN_PWMB = 13;
const int PIN_BIN1 = 14;
const int PIN_BIN2 = 12;

// Standby pin
const int PIN_STBY = 27;

// Tốc độ cơ bản (0–255)
const int MOTOR_BASE_SPEED = 200;
