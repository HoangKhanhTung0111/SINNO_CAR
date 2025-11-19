// motor_driver.cpp
#include "motor_driver.h"

// Khởi tạo chân & bật STBY
void motor_driver_init() {
    pinMode(PIN_AIN1, OUTPUT);
    pinMode(PIN_AIN2, OUTPUT);
    pinMode(PIN_PWMA, OUTPUT);

    pinMode(PIN_BIN1, OUTPUT);
    pinMode(PIN_BIN2, OUTPUT);
    pinMode(PIN_PWMB, OUTPUT);

    pinMode(PIN_STBY, OUTPUT);

    // Enable driver
    digitalWrite(PIN_STBY, HIGH);

    motor_stop();
}

// Dừng cả 2 motor
void motor_stop() {
    // Tắt PWM
    analogWrite(PIN_PWMA, 0);
    analogWrite(PIN_PWMB, 0);

    // Có thể để INx = LOW (free-run): 
    digitalWrite(PIN_AIN1, LOW);
    digitalWrite(PIN_AIN2, LOW);
    digitalWrite(PIN_BIN1, LOW);
    digitalWrite(PIN_BIN2, LOW);
}

// Cả 2 bánh tiến thẳng (giống case right=1, left=1)
void motor_forward() {
    // Hướng forward: IN1=1, IN2=0 như code IMU
    digitalWrite(PIN_AIN1, HIGH);
    digitalWrite(PIN_AIN2, LOW);
    digitalWrite(PIN_BIN1, HIGH);
    digitalWrite(PIN_BIN2, LOW);

    analogWrite(PIN_PWMA, MOTOR_BASE_SPEED);   // Motor A chạy
    analogWrite(PIN_PWMB, MOTOR_BASE_SPEED);   // Motor B chạy
}

// Rẽ trái: chỉ motor A chạy, motor B dừng (giống right=1, left=0)
void motor_left() {
    // Hướng forward
    digitalWrite(PIN_AIN1, HIGH);
    digitalWrite(PIN_AIN2, LOW);
    digitalWrite(PIN_BIN1, HIGH);
    digitalWrite(PIN_BIN2, LOW);

    analogWrite(PIN_PWMA, MOTOR_BASE_SPEED);   // Motor A chạy
    analogWrite(PIN_PWMB, 0);                  // Motor B dừng
}

// Rẽ phải: chỉ motor B chạy, motor A dừng (giống right=0, left=1)
void motor_right() {
    // Hướng forward
    digitalWrite(PIN_AIN1, HIGH);
    digitalWrite(PIN_AIN2, LOW);
    digitalWrite(PIN_BIN1, HIGH);
    digitalWrite(PIN_BIN2, LOW);

    analogWrite(PIN_PWMA, 0);                  // Motor A dừng
    analogWrite(PIN_PWMB, MOTOR_BASE_SPEED);   // Motor B chạy
}
