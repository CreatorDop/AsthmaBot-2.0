from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[1];IN=R/'qa/video_frames';OUT=R/'qa/video_composed';OUT.mkdir(exist_ok=True);(R/'video').mkdir(exist_ok=True)
coords=json.loads((R/'qa/video_labels.json').read_text())
def font(size,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)
labels=['Кришка корпусу','OLED-дисплей','ESP32','Акумулятор 18650','Датчик SDP810','Канал PeakFlow','Діафрагма Ø32','Основа корпусу']
for outidx,frame in enumerate(range(1,241,2),1):
 im=Image.new('RGB',(1920,1080),'#111f38');d=ImageDraw.Draw(im)
 d.rectangle((0,0,18,1080),fill='#00b9bd');d.text((64,35),'ASTHMABOT 2.0',font=font(52,True),fill='white');d.text((66,103),'Модульний пристрій · розбирання на основні вузли',font=font(26),fill='#b9cee1')
 phase='Зібраний прилад' if frame<37 else 'Розділення вузлів' if frame<147 else 'Основні компоненти' if frame<195 else 'Зворотне складання'
 d.rounded_rectangle((65,158,630,207),radius=16,fill='#203651');d.text((85,166),phase,font=font(25,True),fill='#28dbc0')
 layer=Image.open(IN/f'{frame:04d}.png').convert('RGBA').resize((1248,858),Image.Resampling.LANCZOS);im.paste(layer,(60,140),layer);d=ImageDraw.Draw(im)
 d.line((1435,240,1435,905),fill='#30435f',width=2)
 d.text((1480,247),'СКЛАД ПРИЛАДУ',font=font(25,True),fill='#28dbc0')
 for i,t in enumerate(labels):
  y=308+i*67;d.ellipse((1480,y,1518,y+38),fill='#7454ef');d.text((1492,y+5),str(i+1),font=font(21,True),fill='white');d.text((1534,y+4),t,font=font(23),fill='#e1ecf6')
 if frame>=110 and frame<=205:
  for i,(x,y) in enumerate(coords[str(frame)]):
   x=60+x*1.3;y=140+y*1.3
   if i==7:x-=100
   if 30<x<1400 and 220<y<970:
    d.ellipse((x-17,y-17,x+17,y+17),fill='#7454ef',outline='white',width=2);d.text((x-7,y-12),str(i+1),font=font(19,True),fill='white')
 d.rectangle((65,1000,1855,1003),fill='#30435f');d.rectangle((65,1000,65+1790*frame/240,1003),fill='#00b9bd')
 d.text((65,1023),'3D-візуалізація CAD · електронні вузли спрощені · фізичний прототип не виготовлено',font=font(20),fill='#b4c5d8')
 im.save(OUT/f'{outidx:04d}.png')
 if frame==161:im.save(R/'video/AsthmaBot2_video_poster.png')
print('120 composed frames, 10 seconds at12fps; interpolate to24fps for delivery')
