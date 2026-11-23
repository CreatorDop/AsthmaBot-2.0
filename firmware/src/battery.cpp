#include "app.h"
namespace ab {
BatteryStatus batteryRead() {
  uint32_t mv = 0;
  for (int i = 0; i < 8; i++)
    mv += analogReadMilliVolts(BATTERY_ADC);
  float v = mv / 8.0f / 1000.0f * 2;
  BatteryStatus b;
  b.volts = v;
  b.valid = v > 2.0f && v < 4.4f;
  b.low = !b.valid || v < 3.35f;
  b.percent = std::max(0, std::min(100, int((v - 3.3f) / .9f * 100)));
  return b;
}
} // namespace ab
