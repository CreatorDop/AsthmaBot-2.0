# Візуалізація розбирання

AsthmaBot2_exploded.mp4 — анімація основних вузлів на основі власних CAD-файлів. Кришка, дисплей, ESP32, акумулятор, SDP810, половини каналу й діафрагма розходяться та повертаються на місця. Електронні плати показані спрощеними габаритними блоками; проводи, ущільнення та гвинти не анімовано.

Це візуальне пояснення конструкції, не запис фізичного прототипу й не покрокова інструкція сервісного розбирання. У Blender-файлі cad/AsthmaBot2_exploded_animation.blend можна змінити камеру, кольори й ключові кадри.

Відтворення відео:

```sh
blender -b -t 4 -P tools/make_video.py
python tools/compose_video.py
ffmpeg -y -framerate 12 -i qa/video_composed/%04d.png -vf "minterpolate=fps=24:mi_mode=blend,format=yuv420p" -c:v libx264 -crf 19 -preset medium -movflags +faststart video/AsthmaBot2_exploded.mp4
```

Шкала240кадрів при24fps; рендер кожного другого кадру та інтерполяція до24fps. Звуку немає.
