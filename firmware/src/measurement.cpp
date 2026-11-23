#include "core.h"
#include <cstring>
namespace ab {
bool validCalibration(const Calibration &c) {
  if (c.count < 3 || c.count > 12 || c.module != 2 || c.id[0] == 0 ||
      !memchr(c.id, 0, sizeof(c.id)))
    return false;
  for (const char *p = c.id; *p; p++)
    if (!((*p >= 'A' && *p <= 'Z') || (*p >= 'a' && *p <= 'z') ||
          (*p >= '0' && *p <= '9') || *p == '-' || *p == '_'))
      return false;
  if (c.points[0].pa != 0 || c.points[0].lpm != 0)
    return false;
  for (unsigned i = 0; i < c.count; i++) {
    auto p = c.points[i];
    if (!std::isfinite(p.pa) || !std::isfinite(p.lpm) || p.pa < 0 ||
        p.pa > 450 || p.lpm < 0 || p.lpm > 1000)
      return false;
    if (i && (p.pa <= c.points[i - 1].pa || p.lpm <= c.points[i - 1].lpm))
      return false;
  }
  return true;
}
bool convertPressure(const Calibration &c, float pa, float &lpm) {
  if (!validCalibration(c) || !std::isfinite(pa) || pa < 0 ||
      pa > c.points[c.count - 1].pa)
    return false;
  for (unsigned i = 1; i < c.count; i++)
    if (pa <= c.points[i].pa) {
      auto a = c.points[i - 1], b = c.points[i];
      lpm = a.lpm + (pa - a.pa) * (b.lpm - a.lpm) / (b.pa - a.pa);
      return true;
    }
  return false;
}
uint8_t crc8(const uint8_t *d, size_t n) {
  uint8_t c = 0xFF;
  for (size_t i = 0; i < n; i++) {
    c ^= d[i];
    for (int b = 0; b < 8; b++)
      c = c & 0x80 ? uint8_t((c << 1) ^ 0x31) : uint8_t(c << 1);
  }
  return c;
}
const char *errorCode(Error e) {
  static const char *names[] = {
      "OK",    "NO_SENSOR", "CRC",     "RANGE",   "NO_CAL", "MODULE", "TIMING",
      "SHORT", "TIMEOUT",   "REVERSE", "STORAGE", "ZERO",   "BATTERY"};
  return names[unsigned(e) < 13 ? unsigned(e) : 1];
}
Repeatability repeatability(const float *r, size_t n, float tol) {
  Repeatability out;
  if (n < 3 || !std::isfinite(tol) || tol < 0)
    return out;
  float a = 0, b = 0;
  for (size_t i = 0; i < n; i++) {
    if (!std::isfinite(r[i]) || r[i] <= 0)
      return out;
    if (r[i] >= a) {
      b = a;
      a = r[i];
    } else
      b = std::max(b, r[i]);
  }
  out = {true, a - b <= tol, a, a - b};
  return out;
}
float relativePercent(float r, float b) {
  return std::isfinite(r) && std::isfinite(b) && r >= 0 && b > 0 ? r / b * 100
                                                                 : NAN;
}
Module identifyModule(float r) {
  if (r > .06f && r < .13f)
    return Module::Basic;
  if (r > .27f && r < .37f)
    return Module::Peak;
  if (r > .44f && r < .56f)
    return Module::Nasal;
  return Module::Unknown;
}
void Measurement::begin(uint32_t now) {
  state_ = State::Waiting;
  error_ = Error::None;
  began_ = last_ = onset_ = lastFlow_ = now;
  peak_ = 0;
  samples_ = 0;
}
void Measurement::fail(Error e) {
  error_ = e;
  state_ = State::Fault;
}
void Measurement::sample(float q, uint32_t now) {
  if (state_ != State::Waiting && state_ != State::Capture)
    return;
  if (now - last_ > 25) {
    fail(Error::Timing);
    return;
  }
  last_ = now;
  if (!std::isfinite(q) || q > 1000) {
    fail(Error::Range);
    return;
  }
  if (q < -15) {
    fail(Error::Reverse);
    return;
  }
  if (state_ == State::Waiting) {
    if (now - began_ > 15000) {
      fail(Error::Timeout);
      return;
    }
    if (q >= 15) {
      state_ = State::Capture;
      onset_ = now;
      lastFlow_ = now;
      peak_ = q;
      samples_ = 1;
    }
    return;
  }
  peak_ = std::max(peak_, q);
  samples_++;
  if (q >= 5)
    lastFlow_ = now;
  if (now - lastFlow_ >= 300 || now - onset_ >= 6000) {
    if (lastFlow_ - onset_ < 100 || samples_ < 20) {
      fail(Error::TooShort);
      return;
    }
    state_ = State::Done;
  }
}
} // namespace ab
