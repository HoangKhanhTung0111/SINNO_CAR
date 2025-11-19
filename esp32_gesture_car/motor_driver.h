// motor_driver.h
#pragma once

#include <Arduino.h>
#include "config.h"

void motor_driver_init();
void motor_forward();
void motor_left();
void motor_right();
void motor_stop();
