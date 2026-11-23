#include "app.h"
#include <ArduinoJson.h>
#include <cstring>
using namespace ab;
namespace {
Settings settings;
Calibration calibration;
Measurement measure;
BatteryStatus battery;
enum class Screen : uint8_t {
  Menu,
  Profile,
  History,
  Settings,
  Zero,
  Measure,
  Result,
  Exercise
};
Screen screen = Screen::Menu;
uint8_t menu = 0;
bool demo = false;
Error fault = Error::None;
bool sensorOK = false, storageOK = false;
uint32_t measureStart = 0;
uint32_t sampleAt = 0, uiAt = 0, zeroAt = 0, clockEpoch = 0, clockAt = 0;
float zeroSum = 0, zeroSq = 0, zeroOffset = 0;
int zeroN = 0;
Module module = Module::Unknown;
float sessionResults[3]{};
uint8_t sessionCount = 0;
bool sessionDemo = false;
char sessionCal[32]{};
Record latest;
String serialLine;
String message;
struct Button {
  int pin;
  bool raw = true, stable = true;
  uint32_t changed = 0;
  bool pressed() {
    bool v = digitalRead(pin);
    if (v != raw) {
      raw = v;
      changed = millis();
    }
    if (v != stable && millis() - changed >= 25) {
      stable = v;
      return !v;
    }
    return false;
  }
};
Button next{BTN_NEXT}, ok{BTN_OK}, back{BTN_BACK};
uint32_t epochNow() {
  return clockEpoch ? clockEpoch + (millis() - clockAt) / 1000 : 0;
}
void reply(const String &s, bool ble) {
  if (ble)
    bluetoothSend(s);
  else
    Serial.println(s);
}
void resetSession() {
  sessionCount = 0;
  memset(sessionResults, 0, sizeof(sessionResults));
  sessionDemo = demo;
  strlcpy(sessionCal, calibration.id, sizeof(sessionCal));
}
void beginMeasure() {
  fault = Error::None;
  message = "";
  battery = batteryRead();
  module = sensorsModule();
  if (!demo) {
    if (!storageOK) {
      fault = Error::Storage;
    } else if (!battery.valid || battery.low) {
      fault = Error::LowBattery;
    } else if (module != Module::Peak) {
      fault = Error::WrongModule;
    } else if (!validCalibration(calibration)) {
      fault = Error::NoCalibration;
    } else {
      sensorOK = sensorsBegin();
      if (!sensorOK)
        fault = Error::NoSensor;
    }
  }
  if (fault != Error::None) {
    screen = Screen::Result;
    return;
  }
  if (sessionDemo != demo || strcmp(sessionCal, calibration.id))
    resetSession();
  displayLines(demo ? "ДЕМО / тест" : "СТЕНД / PEF", "Не змінюйте насадку",
               demo ? "Штучний сигнал" : "Нуль: без потоку");
  sampleAt = millis();
  if (demo) {
    measureStart = sampleAt;
    measure.begin(sampleAt);
    screen = Screen::Measure;
  } else {
    zeroSum = zeroSq = 0;
    zeroN = 0;
    zeroAt = millis();
    screen = Screen::Zero;
  }
}
void processCommand(const String &line, bool ble) {
  JsonDocument d;
  if (deserializeJson(d, line)) {
    reply("{\"error\":\"JSON\"}", ble);
    return;
  }
  String cmd = d["cmd"] | "";
  // Під час збору не виконуємо довгі операції I/O: вони спотворили б максимум
  // PEF.
  if (screen == Screen::Measure || screen == Screen::Zero) {
    reply("{\"error\":\"BUSY\"}", ble);
    return;
  }
  if (cmd == "history") {
    Record r;
    for (size_t i = 0; i < historyCount(); i++)
      if (historyGet(i, r))
        reply(recordJson(r), ble);
    reply("{\"type\":\"end\"}", ble);
  } else if (cmd == "status") {
    JsonDocument o;
    o["type"] = "status";
    o["version"] = "2.0.0-lab";
    o["calibrated"] = validCalibration(calibration);
    o["cal"] = calibration.id;
    o["demo"] = demo;
    o["profile"] = settings.profile;
    o["baseline"] = settings.baseline;
    o["baseline_cal"] = settings.baselineCal;
    o["battery_v"] = battery.volts;
    o["module"] = uint8_t(module);
    String s;
    serializeJson(o, s);
    reply(s, ble);
  } else if (cmd == "time") {
    uint32_t e = d["epoch"] | 0U;
    if (e < 1577836800U || e > 4102444800U) {
      reply("{\"error\":\"TIME\"}", ble);
      return;
    }
    clockEpoch = e;
    clockAt = millis();
    reply("{\"ok\":\"time\"}", ble);
  } else if (cmd == "profile") {
    int p = d["id"] | -1;
    if (p < 0 || p > 6) {
      reply("{\"error\":\"PROFILE\"}", ble);
      return;
    }
    settings.profile = p;
    if (!saveSettings(settings)) {
      reply("{\"error\":\"STORAGE\"}", ble);
      return;
    }
    resetSession();
    reply("{\"ok\":\"profile\"}", ble);
  } else if (cmd == "calibrate" && !ble) {
    Calibration c;
    const char *calName = d["id"] | "";
    if (strlen(calName) >= sizeof(c.id)) {
      reply("{\"error\":\"CAL_ID\"}", ble);
      return;
    }
    strlcpy(c.id, calName, sizeof(c.id));
    c.module = 2;
    JsonArray a = d["points"].as<JsonArray>();
    if (a.size() > 12) {
      reply("{\"error\":\"CAL\"}", ble);
      return;
    }
    c.count = a.size();
    for (unsigned i = 0; i < c.count; i++) {
      c.points[i].pa = a[i][0] | NAN;
      c.points[i].lpm = a[i][1] | NAN;
    }
    if (!validCalibration(c) || !saveCalibration(c)) {
      reply("{\"error\":\"CAL\"}", ble);
      return;
    }
    calibration = c;
    settings.baseline = 0;
    settings.baselineCal[0] = 0;
    saveSettings(settings);
    resetSession();
    reply("{\"ok\":\"calibration\",\"clinical\":false}", ble);
  } else if (cmd == "baseline" && !ble) {
    float v = d["value"] | NAN;
    const char *id = d["cal"] | "";
    if (!validCalibration(calibration) || strcmp(id, calibration.id) ||
        !std::isfinite(v) || v <= 0 ||
        v > calibration.points[calibration.count - 1].lpm) {
      reply("{\"error\":\"BASELINE\"}", ble);
      return;
    }
    settings.baseline = v;
    strlcpy(settings.baselineCal, id, 32);
    reply(saveSettings(settings) ? "{\"ok\":\"baseline\"}"
                                 : "{\"error\":\"STORAGE\"}",
          ble);
  } else if (cmd == "repeat_tolerance" && !ble) {
    float v = d["lpm"] | NAN;
    if (!std::isfinite(v) || v < 0 || v > 100) {
      reply("{\"error\":\"TOLERANCE\"}", ble);
      return;
    }
    settings.repeatTolerance = v;
    reply(saveSettings(settings) ? "{\"ok\":\"tolerance\"}"
                                 : "{\"error\":\"STORAGE\"}",
          ble);
  } else if (cmd == "nasal") {
    float v = nasalRaw();
    reply(String("{\"type\":\"nasal\",\"mv\":") +
              (sensorsModule() == Module::Nasal && std::isfinite(v)
                   ? String(v, 1)
                   : "null") +
              ",\"uptime_ms\":" + String(millis()) + "}",
          ble);
  } else if (cmd == "raw" && !ble) {
    auto r = sensorsRead();
    reply(String("{\"pa\":") +
              (r.error == Error::None ? String(r.pa, 4) : "null") +
              ",\"error\":\"" + errorCode(r.error) + "\"}",
          ble);
  } else
    reply("{\"error\":\"COMMAND_NOT_ALLOWED\"}", ble);
}
void sample() {
  uint32_t now = millis();
  if (int32_t(now - sampleAt) < 0)
    return;
  sampleAt = now + 5;
  if (screen == Screen::Zero) {
    auto r = sensorsRead();
    if (r.error != Error::None) {
      fault = r.error;
      screen = Screen::Result;
      return;
    }
    zeroSum += r.pa;
    zeroSq += r.pa * r.pa;
    zeroN++;
    if (now - zeroAt >= 2000) {
      float mean = zeroSum / zeroN;
      float sd = sqrtf(std::max(0.0f, zeroSq / zeroN - mean * mean));
      if (zeroN < 300 || fabsf(mean) > 2 || sd > .2f) {
        fault = Error::Zero;
        screen = Screen::Result;
        return;
      }
      zeroOffset = mean;
      displayLines("СТЕНД / запис", "Контрольований потік",
                   "НАЗАД = скасувати");
      now = millis();
      measure.begin(now);
      screen = Screen::Measure;
      sampleAt = now + 5;
    }
    return;
  }
  if (screen != Screen::Measure)
    return;
  static uint32_t moduleAt = 0;
  if (!demo && now - moduleAt >= 100) {
    moduleAt = now;
    if (sensorsModule() != Module::Peak) {
      measure.fail(Error::WrongModule);
    }
  }
  float q = 0;
  if (demo) {
    float t = float(now - measureStart) /
              1000; // час заданого сценарію, не випадковий результат
    q = (t >= 1 && t < 3.7)
            ? 480.0f * (1 - expf(-(t - 1) * 18)) * expf(-.9f * (t - 1))
            : 0;
  } else {
    auto r = sensorsRead();
    if (r.error != Error::None)
      measure.fail(r.error);
    else {
      float pa = r.pa - zeroOffset;
      if (pa < -.8f)
        measure.fail(Error::Reverse);
      else if (!convertPressure(calibration, std::max(0.0f, pa), q))
        measure.fail(Error::Range);
    }
  }
  if (measure.state() != Measurement::State::Fault)
    measure.sample(q, now);
  if (measure.state() == Measurement::State::Fault) {
    fault = measure.error();
    screen = Screen::Result;
    return;
  }
  if (measure.state() == Measurement::State::Done) {
    latest = Record{};
    latest.pef = measure.peak();
    latest.durationMs = measure.duration();
    latest.epoch = epochNow();
    latest.uptimeMs = now;
    latest.demo = demo;
    latest.profile = settings.profile;
    latest.module = 2;
    strlcpy(latest.calibration, demo ? "DEMO-SYNTHETIC" : calibration.id, 32);
    if (!storeRecord(latest)) {
      fault = Error::Storage;
      screen = Screen::Result;
      return;
    }
    sessionResults[sessionCount % 3] = latest.pef;
    sessionCount = std::min<int>(sessionCount + 1, 3);
    screen = Screen::Result;
    Serial.println(recordJson(latest));
    bluetoothSend(recordJson(latest));
  }
}
void show() {
  battery = batteryRead();
  module = sensorsModule();
  switch (screen) {
  case Screen::Menu:
    displayMenu(menu, demo, battery);
    break;
  case Screen::Profile:
    displayLines("Мій профіль", profileAt(settings.profile).name,
                 "Далі: змінити", "ОК: зберегти");
    break;
  case Screen::Settings:
    displayLines("Налаштування", demo ? "ДЕМО: увімкнено" : "ДЕМО: вимкнено",
                 "ОК: перемкнути", "USB: ПЗ / калібр.");
    break;
  case Screen::History: {
    Record r;
    if (historyCount() && historyGet(historyCount() - 1, r))
      displayLines("Історія: остання", String(r.pef, 1) + " л/хв",
                   r.demo ? "ДЕМО" : "СТЕНД / не клініка", "Повна: Bluetooth");
    else
      displayLines("Історія", "Ще немає записів");
    break;
  }
  case Screen::Exercise:
    if (module == Module::Nasal) {
      float v = nasalRaw();
      displayLines("NasalTrack / експ.",
                   std::isfinite(v) ? String(v, 0) + " мВ" : "Датчик відсутній",
                   "Сирий сигнал", "Без оцінки нападів");
    } else
      displayLines("Дихальні вправи", "Без навантаження", "Навчальний режим",
                   "Не під час нападу");
    break;
  case Screen::Result:
    if (fault != Error::None)
      displayLines("Спроба недійсна", errorCode(fault), "ОК: повторити",
                   "НАЗАД: меню");
    else {
      auto r =
          repeatability(sessionResults, sessionCount, settings.repeatTolerance);
      String info =
          String(sessionCount) + "/3: " +
          (r.complete ? (r.repeatable ? "повторювані" : "розкид завеликий")
                      : "ще спроби");
      float pct = relativePercent(latest.pef, settings.baseline);
      String rel = !demo && strcmp(settings.baselineCal, calibration.id) == 0 &&
                           std::isfinite(pct)
                       ? String(pct, 0) + "% власної бази"
                       : "ДЕМО/СТЕНД";
      displayLines(String(latest.pef, 1) + " л/хв", info, rel,
                   "ОК: ще / НАЗАД");
    }
    break;
  default:
    break;
  }
}
} // namespace
void setup() {
  Serial.begin(115200);
  diagnosticsBegin();
  storageOK = storageBegin();
  settings = loadSettings();
  calibration = loadCalibration();
  sensorOK = sensorsBegin();
  displayBegin();
  bluetoothBegin();
  battery = batteryRead();
  module = sensorsModule();
  displayLines("ASTHMABOT 2.0", "Стендовий прототип",
               "Гостра задишка:", "за планом лікаря");
  delay(2200);
}
void loop() {
  bool n = next.pressed(), o = ok.pressed(), b = back.pressed();
  bool capturing = screen == Screen::Zero || screen == Screen::Measure;
  if (b) {
    screen = Screen::Menu;
    fault = Error::None;
  }
  if (!capturing) {
    if (screen == Screen::Menu) {
      if (n)
        menu = (menu + 1) % 6;
      if (o) {
        switch (menu) {
        case 0:
          measureStart = millis();
          beginMeasure();
          break;
        case 1:
          screen = Screen::History;
          break;
        case 2:
          screen = Screen::Profile;
          break;
        case 3:
          screen = Screen::Exercise;
          break;
        case 4:
          bluetoothEnable(!bluetoothEnabled());
          message = bluetoothEnabled() ? "BLE ON" : "BLE OFF";
          displayLines("Bluetooth", message, "Лише тестові дані");
          delay(500);
          break;
        case 5:
          screen = Screen::Settings;
          break;
        }
      }
    } else if (screen == Screen::Profile) {
      if (n)
        settings.profile = (settings.profile + 1) % 7;
      if (o) {
        saveSettings(settings);
        resetSession();
        screen = Screen::Menu;
      }
    } else if (screen == Screen::Settings && o) {
      demo = !demo;
      resetSession();
    } else if (screen == Screen::Result && o) {
      if (sessionCount == 3)
        resetSession();
      measureStart = millis();
      beginMeasure();
    }
    if (screen != Screen::Measure && screen != Screen::Zero) {
      while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
          processCommand(serialLine, false);
          serialLine = "";
        } else if (c != '\r') {
          if (serialLine.length() < 1800)
            serialLine += c;
          else
            serialLine = "";
        }
      }
      auto cmd = bluetoothCommand();
      if (cmd.length())
        processCommand(cmd, true);
    }
  }
  sample();
  diagnosticsShow(fault, screen == Screen::Measure);
  if (screen != Screen::Measure && screen != Screen::Zero &&
      millis() - uiAt > 180) {
    uiAt = millis();
    show();
  }
  delay(1);
}
