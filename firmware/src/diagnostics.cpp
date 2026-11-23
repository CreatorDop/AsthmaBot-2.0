#include "app.h"
namespace ab {
void diagnosticsBegin() {
  for (int p : {LED_OK, LED_ERR, BUZZER}) {
    pinMode(p, OUTPUT);
    digitalWrite(p, LOW);
  }
  for (int p : {BTN_NEXT, BTN_OK, BTN_BACK})
    pinMode(p, INPUT_PULLUP);
  analogReadResolution(12);
  analogSetPinAttenuation(BATTERY_ADC, ADC_11db);
  analogSetPinAttenuation(MODULE_ADC, ADC_11db);
  analogSetPinAttenuation(NASAL_ADC, ADC_11db);
}
void diagnosticsShow(Error e, bool active) {
  digitalWrite(LED_ERR, e != Error::None);
  digitalWrite(LED_OK, e == Error::None && active);
  static Error previous = Error::None;
  static uint32_t off = 0;
  if (e != previous && e != Error::None) {
    digitalWrite(BUZZER, HIGH);
    off = millis() + 80;
  }
  if (off && int32_t(millis() - off) >= 0) {
    digitalWrite(BUZZER, LOW);
    off = 0;
  }
  previous = e;
}
} // namespace ab
