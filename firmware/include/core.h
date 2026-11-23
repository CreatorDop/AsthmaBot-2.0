#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
namespace ab {
constexpr uint16_t VERSION = 2;
enum class Module : uint8_t { Unknown = 0, Basic = 1, Peak = 2, Nasal = 3 };
enum class Error : uint8_t {
  None = 0,
  NoSensor,
  Crc,
  Range,
  NoCalibration,
  WrongModule,
  Timing,
  TooShort,
  Timeout,
  Reverse,
  Storage,
  Zero,
  LowBattery
};
struct CalPoint {
  float pa = 0, lpm = 0;
};
struct Calibration {
  char id[32]{};
  uint8_t count = 0;
  uint8_t module = 2;
  CalPoint points[12]{};
};
struct Record {
  uint32_t sequence = 0, epoch = 0, uptimeMs = 0, durationMs = 0;
  float pef = 0;
  uint8_t profile = 0, module = 2;
  bool demo = false;
  char calibration[32]{};
};
struct Settings {
  uint16_t version = VERSION;
  uint8_t profile = 0;
  float baseline = 0;
  char baselineCal[32]{};
  float repeatTolerance = 20;
};
bool validCalibration(const Calibration &c);
bool convertPressure(const Calibration &c, float pa, float &lpm);
uint8_t crc8(const uint8_t *data, size_t len);
const char *errorCode(Error e);
struct Repeatability {
  bool complete = false, repeatable = false;
  float best = 0, difference = 0;
};
Repeatability repeatability(const float *results, size_t count,
                            float tolerance);
float relativePercent(float result, float baseline);
// Ідентифікація насадки: 10 кОм до 3V3; резистор насадки до GND.
Module identifyModule(float ratio);
class Measurement {
public:
  enum class State : uint8_t { Idle, Waiting, Capture, Done, Fault };
  void begin(uint32_t now);
  void sample(float flow, uint32_t now);
  void fail(Error e);
  State state() const { return state_; }
  float peak() const { return peak_; }
  uint32_t duration() const { return lastFlow_ - onset_; }
  Error error() const { return error_; }

private:
  State state_ = State::Idle;
  Error error_ = Error::None;
  uint32_t began_ = 0, last_ = 0, onset_ = 0, lastFlow_ = 0;
  float peak_ = 0;
  uint16_t samples_ = 0;
};
} // namespace ab
