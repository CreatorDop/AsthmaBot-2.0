#include "app.h"
#include <ArduinoJson.h>
#include <Preferences.h>
namespace ab {
static Preferences prefs;
static bool available = false;
static Record records[96];
static uint16_t count = 0;
static uint32_t sequence = 0;
struct SavedRecord {
  uint32_t magic = 0x41423231;
  Record record{};
  uint32_t crc = 0;
};
static uint32_t checksum(const Record &r) {
  uint32_t c = 0xffffffff;
  const auto *p = reinterpret_cast<const uint8_t *>(&r);
  for (size_t i = 0; i < sizeof(r); i++) {
    c ^= p[i];
    for (int b = 0; b < 8; b++)
      c = (c >> 1) ^ (0xedb88320U & uint32_t(-int32_t(c & 1)));
  }
  return ~c;
}
static bool validRecord(const Record &r) {
  return r.sequence > 0 && r.profile < 7 && r.module == 2 &&
         std::isfinite(r.pef) && r.pef > 0 && r.pef <= 1000 &&
         r.calibration[0] && r.calibration[31] == 0;
}
bool storageBegin() {
  available = prefs.begin("asthmabot2", false);
  if (!available)
    return false;
  // Кожен слот — один атомарний запис NVS. Порядок відновлюється з sequence;
  // окремого лічильника, який міг би відстати після вимкнення, немає.
  bool intact = true;
  count = 0;
  sequence = 0;
  for (unsigned i = 0; i < 96; i++) {
    char key[10];
    snprintf(key, sizeof(key), "slot%u", i);
    size_t n = prefs.getBytesLength(key);
    if (!n)
      continue;
    SavedRecord item{};
    if (n != sizeof(item) ||
        prefs.getBytes(key, &item, sizeof(item)) != sizeof(item)) {
      intact = false;
      continue;
    }
    if (item.magic != 0x41423231 || !validRecord(item.record) ||
        item.crc != checksum(item.record)) {
      intact = false;
      continue;
    }
    records[count++] = item.record;
    sequence = std::max(sequence, item.record.sequence);
  }
  std::sort(records, records + count, [](const Record &a, const Record &b) {
    return a.sequence < b.sequence;
  });
  return intact;
}
bool storeRecord(Record &r) {
  if (!available || sequence == UINT32_MAX)
    return false;
  r.sequence = sequence + 1;
  if (!validRecord(r))
    return false;
  SavedRecord item{};
  item.record = r;
  item.crc = checksum(item.record);
  char key[10];
  snprintf(key, sizeof(key), "slot%u", (r.sequence - 1) % 96);
  if (prefs.putBytes(key, &item, sizeof(item)) != sizeof(item))
    return false;
  // Оперативну історію змінюємо лише після успішного збереження.
  sequence = r.sequence;
  if (count == 96) {
    for (unsigned i = 1; i < count; i++)
      records[i - 1] = records[i];
    count--;
  }
  records[count++] = r;
  return true;
}
size_t historyCount() { return count; }
bool historyGet(size_t i, Record &r) {
  if (i >= count)
    return false;
  r = records[i];
  return true;
}
void historyClear() {
  for (unsigned i = 0; i < 96; i++) {
    char key[10];
    snprintf(key, sizeof(key), "slot%u", i);
    prefs.remove(key);
  }
  count = 0;
  sequence = 0;
}
Settings loadSettings() {
  Settings s;
  if (available && prefs.getBytesLength("settings") == sizeof(s))
    prefs.getBytes("settings", &s, sizeof(s));
  if (s.version != VERSION || s.profile > 6 || !std::isfinite(s.baseline) ||
      s.baseline < 0 || s.baseline > 1000 ||
      !std::isfinite(s.repeatTolerance) || s.repeatTolerance < 0 ||
      s.repeatTolerance > 100)
    s = Settings{};
  s.baselineCal[31] = 0;
  return s;
}
bool saveSettings(const Settings &s) {
  return available && prefs.putBytes("settings", &s, sizeof(s)) == sizeof(s);
}
Calibration loadCalibration() {
  Calibration c;
  if (available && prefs.getBytesLength("cal") == sizeof(c))
    prefs.getBytes("cal", &c, sizeof(c));
  if (!validCalibration(c))
    return Calibration{};
  return c;
}
bool saveCalibration(const Calibration &c) {
  return available && validCalibration(c) &&
         prefs.putBytes("cal", &c, sizeof(c)) == sizeof(c);
}
String recordJson(const Record &r) {
  JsonDocument d;
  d["type"] = "record";
  d["seq"] = r.sequence;
  d["epoch"] = r.epoch;
  d["uptime_ms"] = r.uptimeMs;
  d["pef"] = r.pef;
  d["duration_ms"] = r.durationMs;
  d["profile"] = r.profile;
  d["module"] = r.module;
  d["demo"] = r.demo;
  d["cal"] = r.calibration;
  String s;
  serializeJson(d, s);
  return s;
}
} // namespace ab
