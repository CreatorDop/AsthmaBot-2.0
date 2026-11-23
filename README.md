# AsthmaBot 2.0 · LAB

Модульний ESP32-прототип PEF, історії й щоденника. Модернізація попереднього InhaleLab; архів у legacy_inhale_lab/.

**Стан: програмний і механічний прототип. Не сертифікований медичний виріб. Реальних калібрувальних даних і фізичних випробувань немає. При гострій задишці дійте за призначеним лікарем планом невідкладної допомоги; цей прототип не лікує напад.**

## Почати

- Відео: video/AsthmaBot2_exploded.mp4; редагована Blender-сцена в cad/.
- Презентація: presentation/AsthmaBot2_DemoDay.pptx і PDF.
- Повний технічний опис: docs/AsthmaBot2_Engineering.pdf.
- Відкрити автономний web/AsthmaBot2_Demo.html або web/index.html для DEMO без пристрою; BLE потребує HTTPS/localhost і сумісного браузера.
- Збірка прошивки: `pio run -d firmware`; докладно docs/firmware.md.
- Для виготовлення: cad/*.step, *.stl, *.dxf, складальне креслення й A3 PDF. Розміри в mm.
- Схема: hardware/*.kicad_sch, PDF, connections.csv; BOM: hardware/BOM.csv.

## Реалізовано в коді

Драйвер SDP810 з CRC, калібрувальна таблиця й збір піку, відхилення несправних спроб, OLEDменю,7 профілів,96 записівNVS, ручна база, BLEGATT, приблизний заряд, USBоновлення та явний DEMO. WebUI має графіки, щоденник і CSV. Реальна робота з апаратурою ще не підтверджена.

## Документація

[audit](docs/audit.md) · [concept](docs/concept.md) · [PEF](docs/pef_feasibility.md) · [electronics](docs/electronics.md) · [budget](docs/budget.md) · [mechanics](docs/mechanics.md) · [assembly](docs/assembly.md) · [firmware](docs/firmware.md) · [profiles](docs/profiles.md) · [calibration](docs/calibration.md) · [tests](docs/test_plan.md) · [risks](docs/risks_and_standards.md) · [limitations](docs/limitations.md) · [analogues](docs/analogues.md) · [sources](docs/sources.md).

Бюджет не вміщується у2000 грн; деталі й статус цін наведено в кошторисі. Не завантажувати вигадані калібрувальні коефіцієнти. Не об’єднувати DEMO з реальними записами.

## Git

Локальні main і archive/asthmabot-before-2 зберігають вихідну роботу; feature/asthmabot-2 містить модернізацію. Віддалений repository не підключено, PR не створено. Див. docs/github_handoff.md. Злиття у main не виконувалось.

Повна матриця виконання: [feature_status](docs/feature_status.md). Звіт: [TEST_REPORT](qa/TEST_REPORT.md).
