#pragma once
#include "core.h"
#include <Arduino.h>
namespace ab {
constexpr int SENSOR_SDA = 21, SENSOR_SCL = 22, OLED_SDA = 18, OLED_SCL = 19;
constexpr int BTN_NEXT = 32, BTN_OK = 33, BTN_BACK = 25, LED_OK = 26,
              LED_ERR = 27, BUZZER = 13, BATTERY_ADC = 36, MODULE_ADC = 39,
              NASAL_ADC = 34, NASAL_EXCITE = 23;
constexpr const char *SERVICE_UUID = "d0bb0001-86ce-4d45-8c2f-154a1cefe200";
constexpr const char *TX_UUID = "d0bb0002-86ce-4d45-8c2f-154a1cefe200";
constexpr const char *RX_UUID = "d0bb0003-86ce-4d45-8c2f-154a1cefe200";
struct SensorReading {
  float pa = 0, temp = 0;
  Error error = Error::None;
};
struct BatteryStatus {
  float volts = 0;
  int percent = 0;
  bool low = false, valid = false;
};
struct Profile {
  const char *name;
  const char *diary;
};
const Profile &profileAt(uint8_t id);
bool sensorsBegin();
SensorReading sensorsRead();
Module sensorsModule();
float nasalRaw();
bool storageBegin();
bool storeRecord(Record &r);
size_t historyCount();
bool historyGet(size_t i, Record &r);
void historyClear();
Settings loadSettings();
bool saveSettings(const Settings &s);
Calibration loadCalibration();
bool saveCalibration(const Calibration &c);
BatteryStatus batteryRead();
void diagnosticsBegin();
void diagnosticsShow(Error e, bool active);
void displayBegin();
bool displayPresent();
void displayMenu(uint8_t selected, bool demo, const BatteryStatus &b);
void displayLines(const String &title, const String &a, const String &b = "",
                  const String &c = "");
void bluetoothBegin();
void bluetoothEnable(bool enable);
bool bluetoothEnabled();
void bluetoothSend(const String &message);
String bluetoothCommand();
String recordJson(const Record &r);
} // namespace ab
