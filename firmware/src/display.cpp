#include "app.h"
#include <U8g2lib.h>
#include <Wire.h>
namespace ab {
// Другий апаратний I²C: OLED не блокує шину датчика.
static U8G2_SSD1306_128X64_NONAME_F_2ND_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);
static bool present = false;
void displayBegin() {
  Wire1.setPins(OLED_SDA, OLED_SCL);
  oled.begin();
  Wire1.beginTransmission(0x3C);
  present = Wire1.endTransmission() == 0;
  oled.setFont(u8g2_font_6x13_t_cyrillic);
  oled.enableUTF8Print();
}
bool displayPresent() { return present; }
static void row(int y, const String &s) {
  oled.setCursor(0, y);
  oled.print(s);
}
void displayLines(const String &title, const String &a, const String &b,
                  const String &c) {
  if (!present)
    return;
  oled.clearBuffer();
  row(12, title);
  row(29, a);
  row(45, b);
  row(61, c);
  oled.sendBuffer();
}
void displayMenu(uint8_t selected, bool demo, const BatteryStatus &b) {
  static const char *menu[] = {"Виміряти PEF",    "Історія",   "Мій профіль",
                               "Дихальні вправи", "Bluetooth", "Налаштування"};
  if (!present)
    return;
  oled.clearBuffer();
  row(11, "ASTHMABOT 2.0");
  row(25, demo ? "ДЕМО / тестові дані"
               : String(b.volts, 2) + "V ~" + String(b.percent) + "%");
  row(43, String("> ") + menu[selected]);
  row(61, "Далі  ОК  Назад");
  oled.sendBuffer();
}
} // namespace ab
