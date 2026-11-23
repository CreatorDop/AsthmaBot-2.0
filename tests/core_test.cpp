#include "core.h"
#include <cassert>
#include <cstring>
#include <iostream>
using namespace ab;
int main() {
  Calibration c;
  strcpy(c.id, "TEST-ONLY");
  c.count = 4;
  c.points[0] = {0, 0};
  c.points[1] = {1, 50};
  c.points[2] = {25, 250};
  c.points[3] = {100, 500};
  assert(validCalibration(c));
  float q;
  assert(convertPressure(c, 25, q) && q == 250);
  assert(!convertPressure(c, 101, q));
  assert(!convertPressure(c, -1, q));
  assert(!convertPressure(c, NAN, q));
  auto bad = c;
  bad.count = 13;
  assert(!validCalibration(bad));
  bad = c;
  bad.points[2].pa = 1;
  assert(!validCalibration(bad));
  bad = c;
  bad.points[2].lpm = NAN;
  assert(!validCalibration(bad));
  const uint8_t data[] = {0xBE, 0xEF};
  assert(crc8(data, 2) == 0x92);
  assert(identifyModule(.091f) == Module::Basic);
  assert(identifyModule(.32f) == Module::Peak);
  assert(identifyModule(.5f) == Module::Nasal);
  assert(identifyModule(.99f) == Module::Unknown);
  float r[] = {400, 410, 405};
  auto repeat = repeatability(r, 3, 20);
  assert(repeat.complete && repeat.repeatable && repeat.best == 410 &&
         repeat.difference == 5);
  assert(!repeatability(r, 2, 20).complete);
  assert(!repeatability(r, 3, 2).repeatable);
  assert(std::isnan(relativePercent(400, 0)));
  assert(relativePercent(400, 500) == 80);
  Measurement m;
  m.begin(0);
  for (unsigned t = 5; t <= 1200; t += 5)
    m.sample(t < 100 ? 0 : t < 700 ? float(500 - (t - 100) / 2) : 0, t);
  assert(m.state() == Measurement::State::Done);
  assert(m.peak() == 500);
  m.begin(0);
  m.sample(400, 5);
  m.sample(0, 10);
  for (unsigned t = 15; t <= 320; t += 5)
    m.sample(0, t);
  assert(m.error() == Error::TooShort);
  m.begin(0);
  m.sample(0, 40);
  assert(m.error() == Error::Timing);
  m.begin(0);
  m.sample(-20, 5);
  assert(m.error() == Error::Reverse);
  m.begin(0);
  m.sample(NAN, 5);
  assert(m.error() == Error::Range);
  m.begin(0);
  for (unsigned t = 5; t <= 15005; t += 5)
    m.sample(0, t);
  assert(m.error() == Error::Timeout);
  m.begin(0xFFFFFF00);
  for (uint32_t i = 5; i < 1200; i += 5)
    m.sample(i < 600 ? 400 : 0, uint32_t(0xFFFFFF00 + i));
  assert(m.state() == Measurement::State::Done);
  std::cout << "core: calibration/CRC/PEF/faults/repeatability/module/rollover "
               "tests passed\n";
}
