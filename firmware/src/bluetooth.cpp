#include "app.h"
#include <BLE2902.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
namespace ab {
static BLEServer *server = nullptr;
static BLECharacteristic *tx = nullptr;
static bool enabled = false, connected = false;
static QueueHandle_t commands;
struct Message {
  char data[192];
};
class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *) override { connected = true; }
  void onDisconnect(BLEServer *) override {
    connected = false;
    if (enabled)
      BLEDevice::startAdvertising();
  }
};
class RxCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *c) override {
    auto v = c->getValue();
    if (v.size() >= 192)
      return;
    Message m{};
    memcpy(m.data, v.data(), v.size());
    xQueueSend(commands, &m, 0);
  }
};
void bluetoothBegin() {
  commands = xQueueCreate(4, sizeof(Message));
  BLEDevice::init("AsthmaBot2-LAB");
  server = BLEDevice::createServer();
  server->setCallbacks(new ServerCallbacks());
  auto service = server->createService(SERVICE_UUID);
  tx = service->createCharacteristic(TX_UUID,
                                     BLECharacteristic::PROPERTY_NOTIFY |
                                         BLECharacteristic::PROPERTY_READ);
  tx->addDescriptor(new BLE2902());
  auto rx =
      service->createCharacteristic(RX_UUID, BLECharacteristic::PROPERTY_WRITE);
  rx->setCallbacks(new RxCallbacks());
  service->start();
  auto adv = BLEDevice::getAdvertising();
  adv->addServiceUUID(SERVICE_UUID);
  adv->setScanResponse(true);
  BLEDevice::setMTU(185);
}
void bluetoothEnable(bool on) {
  enabled = on;
  if (on)
    BLEDevice::startAdvertising();
  else {
    BLEDevice::stopAdvertising();
    if (connected)
      server->disconnect(server->getConnId());
  }
}
bool bluetoothEnabled() { return enabled; }
void bluetoothSend(const String &input) {
  if (!enabled || !connected || !tx)
    return;
  String data = input + "\n";
  // 20 байтів сумісні з початковим ATT MTU=23; клієнт збирає рядок до \n.
  for (size_t i = 0; i < data.length(); i += 20) {
    size_t n = std::min<size_t>(20, data.length() - i);
    tx->setValue((uint8_t *)data.c_str() + i, n);
    tx->notify();
    delay(12);
  }
}
String bluetoothCommand() {
  Message m{};
  if (commands && xQueueReceive(commands, &m, 0) == pdTRUE)
    return String(m.data);
  return String();
}
} // namespace ab
