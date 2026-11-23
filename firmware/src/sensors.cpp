#include "app.h"
#include <Wire.h>
namespace ab {
static TwoWire sensorBus(0);
static bool ready = false;
static bool command(uint16_t c) {
  sensorBus.beginTransmission(0x25);
  sensorBus.write(c >> 8);
  sensorBus.write(c & 255);
  return sensorBus.endTransmission() == 0;
}
bool sensorsBegin() {
  sensorBus.begin(SENSOR_SDA, SENSOR_SCL, 400000);
  sensorBus.setTimeOut(10);
  delay(30);
  command(0x3FF9);
  delay(2);
  ready = command(0x361E);
  delay(25);
  return ready;
}
SensorReading sensorsRead() {
  SensorReading r;
  if (!ready) {
    r.error = Error::NoSensor;
    return r;
  }
  if (sensorBus.requestFrom(uint8_t(0x25), uint8_t(9)) != 9) {
    r.error = Error::NoSensor;
    while (sensorBus.available())
      sensorBus.read();
    return r;
  }
  uint8_t data[9];
  for (auto &b : data)
    b = sensorBus.read();
  for (int i = 0; i < 9; i += 3)
    if (crc8(data + i, 2) != data[i + 2]) {
      r.error = Error::Crc;
      return r;
    }
  int16_t raw = int16_t((data[0] << 8) | data[1]);
  int16_t temp = int16_t((data[3] << 8) | data[4]);
  uint16_t scale = (data[6] << 8) | data[7];
  // Для SDP810-500Pa очікується масштаб 60 Па^-1. Інший варіант не підміняємо.
  if (scale != 60) {
    r.error = Error::Range;
    return r;
  }
  r.pa = float(raw) / scale;
  r.temp = float(temp) / 200;
  if (!std::isfinite(r.pa) || fabsf(r.pa) >= 490)
    r.error = Error::Range;
  return r;
}
Module sensorsModule() {
  return identifyModule(float(analogReadMilliVolts(MODULE_ADC)) / 3300.0f);
}
float nasalRaw() {
  // BR11KA104N 100 кОм. Імпульсне живлення зменшує самонагрів;
  // R6=100 кОм, C5=10 нФ. Читання лише поза збором PEF.
  pinMode(NASAL_EXCITE, OUTPUT);
  digitalWrite(NASAL_EXCITE, HIGH);
  delay(5);
  float mv = analogReadMilliVolts(NASAL_ADC);
  digitalWrite(NASAL_EXCITE, LOW);
  return mv < 100 || mv > 3000 ? NAN : mv;
}
} // namespace ab
