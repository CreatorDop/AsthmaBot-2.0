from pathlib import Path
import math,json
import cadquery as cq
import ezdxf
from ezdxf.enums import TextEntityAlignment
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
ROOT=Path('/workspace/scratch/cab8eaba5635/inhale_lab'); CAD=ROOT/'cad'; AS=ROOT/'assets'
for p in [CAD,AS]:p.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
# All lengths millimetres. Explicit design proposal, bench-only.
base=cq.Workplane('XY').box(140,100,41,centered=(False,False,False))
base=base.cut(cq.Workplane('XY').box(134,94,40,centered=(False,False,False)).translate((3,3,3)))
for x,y in [(8,8),(132,8),(132,92),(8,92)]:
 p=cq.Workplane('XY').center(x,y).circle(4).extrude(38).translate((0,0,3))
 p=p.cut(cq.Workplane('XY').center(x,y).circle(1.25).extrude(12).translate((0,0,29)))
 base=base.union(p)
# USB left wall and two pneumatic leads plus switch connector right wall
base=base.cut(cq.Workplane('XY').box(6,14,8,centered=(False,False,False)).translate((-1,13,12)))
for y,r in [(35,2.75),(50,2.75),(75,4)]:
 base=base.cut(cq.Workplane('YZ').center(y,20).circle(r).extrude(6).translate((137,0,0)))
lid=cq.Workplane('XY').box(140,100,4,centered=(False,False,False))
lid=lid.cut(cq.Workplane('XY').box(50,38,8,centered=(False,False,False)).translate((45,40,-2)))
for x,y,r in [(8,8,1.7),(132,8,1.7),(132,92,1.7),(8,92,1.7),(35,20,4),(70,20,4),(105,20,4),(38,37,1.1),(102,37,1.1),(38,81,1.1),(102,81,1.1)]:
 lid=lid.cut(cq.Workplane('XY').center(x,y).circle(r).extrude(8).translate((0,0,-2)))
# Pneumatic cassette: two halves, common x axis. 40 mm bodies, 52 mm flanges.
left=cq.Workplane('XY').box(32,40,40,centered=(False,False,False)).translate((0,-20,0))
left=left.union(cq.Workplane('XY').box(4,52,52,centered=(False,False,False)).translate((32,-26,-6)))
left=left.cut(cq.Workplane('YZ').center(0,20).circle(10).extrude(40).translate((-1,0,0)))
left=left.cut(cq.Workplane('YZ').center(0,20).circle(13.2).extrude(1.2).translate((34.8,0,0)))
for y in [-22,22]:
 for z in [-2,42]:left=left.cut(cq.Workplane('YZ').center(y,z).circle(1.7).extrude(6).translate((31,0,0)))
left=left.union(cq.Workplane('XY').center(18,0).circle(2).extrude(8).translate((0,0,40)))
left=left.cut(cq.Workplane('XY').center(18,0).circle(1).extrude(25).translate((0,0,25)))
right=left.mirror('YZ',(36,0,0),union=False)
plate=cq.Workplane('YZ').center(0,20).circle(13).circle(6).extrude(2).translate((35,0,0))
trigger=cq.Workplane('XY').box(45,35,20,centered=(False,False,False))
trigger=trigger.cut(cq.Workplane('XY').box(39,29,17,centered=(False,False,False)).translate((3,3,0)))
trigger=trigger.cut(cq.Workplane('XY').center(22.5,17.5).circle(6).extrude(25))
models={'IL01_console_base':base,'IL02_console_lid':lid,'IL03_flow_left':left,'IL04_flow_right':right,'IL05_orifice_D12':plate,'IL06_trigger_shell':trigger}
for name,obj in models.items():
 cq.exporters.export(obj,str(CAD/(name+'.step')))
 cq.exporters.export(obj,str(CAD/(name+'.stl')),tolerance=.08,angularTolerance=.15)
assert all(o.val().isValid() for o in models.values())
assy=cq.Assembly(name='InhaleLab_Concept_v01')
assy.add(base,name='console_base',color=cq.Color('#04BEBE'))
assy.add(lid.translate((0,0,41)),name='console_lid',color=cq.Color('#F2F5F9'))
assy.add(left.translate((170,50,6)),name='cassette_left',color=cq.Color('#04BEBE'))
assy.add(right.translate((170,50,6)),name='cassette_right',color=cq.Color('#22D5C5'))
assy.add(plate.translate((170,50,6)),name='orifice',color=cq.Color('#FFD549'))
assy.add(trigger.translate((75,-65,0)),name='trigger',color=cq.Color('#7757FF'))
assy.save(str(CAD/'InhaleLab_assembly.step'))
# Exact CAD geometry renders, not a photographed prototype.
def render(parts,name,elev=30,azim=-60):
 fig=plt.figure(figsize=(11,7),dpi=160);ax=fig.add_subplot(111,projection='3d'); coords=[]
 for obj,color in parts:
  v,t=obj.val().tessellate(.25);v=np.array([[p.x,p.y,p.z] for p in v]);faces=v[np.asarray(t)];coords.extend(v)
  rgb=np.array(matplotlib.colors.to_rgb(color));n=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);n=n/(np.linalg.norm(n,axis=1)[:,None]+1e-9)
  light=np.array([-.3,-.4,1]);light/=np.linalg.norm(light);shade=.6+.4*np.clip(n@light,0,1)
  ax.add_collection3d(Poly3DCollection(faces,facecolors=rgb[None,:]*shade[:,None],edgecolors='none',rasterized=True))
 a=np.array(coords);mi=a.min(0);ma=a.max(0);ext=ma-mi
 ax.set_xlim(mi[0]-8,ma[0]+8);ax.set_ylim(mi[1]-8,ma[1]+8);ax.set_zlim(mi[2]-5,ma[2]+5);ax.set_box_aspect(ext)
 ax.view_init(elev=elev,azim=azim);ax.set_axis_off();fig.patch.set_alpha(0);ax.patch.set_alpha(0);plt.subplots_adjust(0,0,1,1)
 plt.savefig(AS/name,transparent=True,bbox_inches='tight',pad_inches=.1);plt.close()
screen=cq.Workplane('XY').box(49,37,1,centered=(False,False,False)).translate((45.5,40.5,43))
buttons=[cq.Workplane('XY').center(x,20).circle(3.7).extrude(3).translate((0,0,43)) for x in (35,70,105)]
parts=[(base,'#04BEBE'),(lid.translate((0,0,41)),'#F2F5F9'),(screen,'#14234A')]+[(o,c) for o,c in zip(buttons,['#FFD549','#7757FF','#FF6258'])]+[(left.translate((170,50,6)),'#04BEBE'),(right.translate((170,50,6)),'#22D5C5'),(plate.translate((170,50,6)),'#FFD549'),(trigger.translate((75,-65,0)),'#7757FF')]
render(parts,'assembly.png')
render([(base,'#04BEBE'),(lid.translate((0,0,75)),'#EDF1F7'),(screen.translate((0,0,34)),'#14234A')],'exploded.png',28,-55)
render([(left,'#04BEBE'),(right.translate((30,0,0)),'#22D5C5'),(plate.translate((15,0,0)),'#FFD549')],'cassette.png',22,-65)
# Unified drawing primitive -> DXF & vector PDF. DXF modelspace 1:1, 5 independent A3 sheets.
MM=72/25.4
pdf=canvas.Canvas(str(CAD/'InhaleLab_Drawings_A3.pdf'),pagesize=(420*MM,297*MM))
pdf.setTitle('InhaleLab — ескізний комплект креслень v0.1')
class Sheet:
 def __init__(self,n,title):
  self.n=n;self.doc=ezdxf.new('R2010');self.doc.units=4;self.m=self.doc.modelspace()
  for layer,color in [('OUTLINE',7),('DIM',4),('CENTER',8),('TEXT',7),('HIDDEN',8),('ELECTRIC',3)]:self.doc.layers.new(layer,dxfattribs={'color':color})
  self.doc.styles.new('UA',dxfattribs={'font':'DejaVuSans.ttf'})
  pdf.saveState();pdf.scale(MM,MM)
  self.rect(10,10,400,277);self.rect(210,10,200,35)
  self.text(216,34,title,4,bold=True);self.text(216,26,f'IL-0{n}   Концепт v0.1   21.11.2026',3)
  self.text(216,18,'Булавин Володимир   КПІ   ПБ-62',3)
  self.text(216,12,f'A3   мм   М 1:1 / вказано   Аркуш {n} із 5',2.6)
  self.text(18,279,'ВДИХ LAB / INHALELAB',5,bold=True)
  self.text(18,272,'Ескізний проєкт. Розміри проєктні. Перед виготовленням перевірити комплектуючі.',2.7)
 def line(self,x1,y1,x2,y2,layer='OUTLINE',w=.3):
  self.m.add_line((x1,y1),(x2,y2),dxfattribs={'layer':layer});pdf.setStrokeColor(HexColor('#68768A' if layer in ['DIM','CENTER','HIDDEN'] else '#15243E'));pdf.setLineWidth(w);pdf.line(x1,y1,x2,y2)
 def rect(self,x,y,w,h,layer='OUTLINE'):
  for a,b,c,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:self.line(a,b,c,d,layer)
 def circle(self,x,y,r,layer='OUTLINE'):
  self.m.add_circle((x,y),r,dxfattribs={'layer':layer});pdf.setStrokeColor(HexColor('#15243E'));pdf.setLineWidth(.25);pdf.circle(x,y,r,stroke=1,fill=0)
 def text(self,x,y,t,h=3,layer='TEXT',bold=False):
  self.m.add_text(t,dxfattribs={'height':h,'layer':layer,'style':'UA'}).set_placement((x,y))
  pdf.setFillColor(HexColor('#15243E'));pdf.setFont('DejaVuBold' if bold else 'DejaVu',h);pdf.drawString(x,y,t)
 def dim(self,x1,y1,x2,y2,off=10,txt=None):
  if y1==y2:
   y=y1+off;self.line(x1,y1,x1,y+2,'DIM',.15);self.line(x2,y2,x2,y+2,'DIM',.15);self.line(x1,y,x2,y,'DIM',.15)
   for x in [x1,x2]:self.line(x-1.4,y-1.4,x+1.4,y+1.4,'DIM',.15)
   self.text((x1+x2)/2-4,y+1.6,txt or f'{abs(x2-x1):g}',3,'DIM')
  else:
   x=x1+off;self.line(x1,y1,x+2,y1,'DIM',.15);self.line(x2,y2,x+2,y2,'DIM',.15);self.line(x,y1,x,y2,'DIM',.15)
   for y in [y1,y2]:self.line(x-1.4,y-1.4,x+1.4,y+1.4,'DIM',.15)
   self.text(x+2,(y1+y2)/2,txt or f'{abs(y2-y1):g}',3,'DIM')
 def notes(self,items,x=20,y=65):
  for i,t in enumerate(items):self.text(x,y-i*5,t,2.8)
 def save(self):
  self.doc.set_modelspace_vport(300,center=(210,148.5));self.doc.saveas(CAD/f'IL-0{self.n}.dxf');pdf.restoreState();pdf.showPage()
s=Sheet(1,'Загальний вигляд пульта')
x,y=35,151;s.rect(x,y,140,100);s.rect(x+45,y+40,50,38)
for a,b in [(8,8),(132,8),(132,92),(8,92)]:s.circle(x+a,y+b,1.7)
for a in [35,70,105]:s.circle(x+a,y+20,4)
s.text(x+49,y+53,'ЕКРАН',5);s.text(x+12,y+105,'Вигляд зверху',3.2);s.dim(x,y,x+140,y,-12);s.dim(x,y,x,y+100,-12)
s.rect(35,79,140,45);s.line(35,120,175,120);s.dim(35,79,175,79,-9);s.dim(175,79,175,124,10);s.text(35,129,'Вигляд спереду',3.2)
s.rect(246,151,100,45)
for a,r in [(35,2.75),(50,2.75),(75,4)]:s.circle(246+a,171,r)
s.line(246,192,346,192);s.dim(246,151,346,151,-10);s.dim(346,151,346,196,12);s.text(246,202,'Права стінка',3.2)
s.text(234,235,'1  Корпус 140 × 100 × 41',3.5);s.text(234,226,'2  Кришка 140 × 100 × 4',3.5);s.text(234,217,'3  Трубки P+ / P− і кнопка',3.5)
s.notes(['1. Габарит пульта у зборі 140 × 100 × 45 мм.','2. Живлення USB 5 В. Електроніка розміщена у сухому відсіку.','3. Плати показані у 3D лише габаритно. Посадки уточнити після закупівлі.'],y=64);s.save()
s=Sheet(2,'Корпус і кришка пульта')
for x,name in [(30,'IL01 Корпус'),(230,'IL02 Кришка')]:
 s.rect(x,151,140,100);s.text(x,257,name,3.5)
 for a,b in [(8,8),(132,8),(132,92),(8,92)]:s.circle(x+a,151+b,4 if x==30 else 1.7)
 s.dim(x,151,x+140,151,-10)
s.rect(33,154,134,94)
for a,b in [(8,8),(132,8),(132,92),(8,92)]:s.circle(30+a,151+b,1.25)
s.rect(275,191,50,38)
for a in [35,70,105]:s.circle(230+a,171,4)
for a,b in [(38,37),(102,37),(38,81),(102,81)]:s.circle(230+a,151+b,1.1)
s.rect(30,87,140,41);s.line(33,90,33,128);s.line(167,90,167,128);s.line(33,90,167,90);s.dim(170,87,170,128,10)
s.rect(230,106,140,4);s.dim(370,106,370,110,10,'4')
s.text(232,95,'Вікно 50 × 38; відступ X45 Y40',3);s.text(232,88,'Кнопки Ø8; X35 / 70 / 105; Y20',3)
s.notes(['Матеріал: PETG для сухого корпусу. Стінка і дно 3 мм.','4 стійки Ø8; пілот Ø2,5 глибиною 12 під самонарізний гвинт.','Кришка: 4 × Ø3,4. Координати осей 8 і 132 по X; 8 і 92 по Y.','Отвори дисплея 4 × Ø2,2 є попередніми; звірити з реальною платою.'],y=75);s.save()
s=Sheet(3,'Пневматична касета')
# drawing enlarged x2 declared geometry model 1:1 in separate actual-size views
x,y=45,166;s.rect(x,y,32,40);s.rect(x+32,y-6,4,52);s.rect(x+36,y-6,4,52);s.rect(x+40,y,32,40)
s.line(x,y+10,x+72,y+10,'HIDDEN');s.line(x,y+30,x+72,y+30,'HIDDEN')
s.line(x-5,y+20,x+77,y+20,'CENTER',.15)
for a in [18,54]:s.rect(x+a-2,y+40,4,8);s.line(x+a,y+25,x+a,y+48,'CENTER',.15)
s.dim(x,y-6,x+72,y-6,-12);s.dim(x+72,y-6,x+72,y+46,14,'52');s.text(x,y+57,'Касета у зборі',3.5)
x2,y2=220,166;s.rect(x2,y2,52,52);s.circle(x2+26,y2+26,10);s.circle(x2+26,y2+26,13.2)
for a in [4,48]:
 for b in [4,48]:s.circle(x2+a,y2+b,1.7)
s.dim(x2,y2,x2+52,y2,-10);s.text(x2-3,y2+58,'Фланець половини',3.5)
s.circle(335,190,13);s.circle(335,190,6);s.text(311,218,'Діафрагма IL05',3.5);s.text(311,166,'Ø26 × 2; отвір Ø12',3)
s.text(35,127,'Розріз вздовж осі потоку',3.5)
s.rect(35,91,72,30);s.rect(35,96,72,20);s.rect(69.8,92.8,2.4,26.4);s.rect(70,93,2,26);s.rect(70,100,2,12)
s.line(20,106,30,106,'CENTER');s.text(116,109,'Кишеня Ø26,4 × 1,2 у кожній половині',3)
s.text(116,101,'Основний канал Ø20. Відбір тиску Ø2.',3);s.text(116,93,'Штуцер Ø4; виступ 8; осі X18 / X54.',3)
s.notes(['1. Кожна половина: тіло 32 × 40 × 40 + фланець 4 × 52 × 52 мм.','2. З’єднання фланців 4 гвинтами M3 × 16 з гайками; ущільнення перевірити.','3. Ø12 діафрагми - стартове проєктне значення. Калібрування обов’язкове.','4. Друкована касета лише для стенда з повітрям. Контакт з пацієнтом не дозволений.'],y=73);s.save()
s=Sheet(4,'Електричні з’єднання')
# Functional connection schematic, explicitly no PCB fabrication claims.
blocks=[(25,191,70,48,'SDP810-500Pa'),(161,168,86,88,'ESP32 DevKit'),(310,191,80,48,'TFT ILI9341'),(25,90,80,46,'USB 5 В'),(161,80,86,46,'КНОПКА ДОЗАТОРА'),(310,90,80,46,'КНОПКИ / ЗУМЕР')]
for x,y,w,h,t in blocks:s.rect(x,y,w,h);s.text(x+4,y+h-9,t,3.5,bold=True)
for i,t in enumerate(['3V3 → VDD','GND → GND','GPIO21 → SDA','GPIO22 → SCL']):s.text(30,220-i*7,t,3)
for i,t in enumerate(['GPIO18 → SCK','GPIO23 → MOSI','GPIO14 → CS','GPIO27 → DC','GPIO26 → RST']):s.text(315,220-i*6,t,3)
s.line(95,211,161,211,'ELECTRIC');s.text(102,216,'I²C 3,3 В',3)
s.line(247,211,310,211,'ELECTRIC');s.text(258,216,'SPI 3,3 В',3)
s.text(168,228,'USB / 5V вхід',3);s.text(168,218,'3V3 живлення логіки',3);s.text(168,198,'Читання 100 Гц*',3);s.text(168,188,'Журнал через USB',3)
s.line(105,112,134,112,'ELECTRIC');s.line(134,112,134,243,'ELECTRIC');s.line(134,243,161,243,'ELECTRIC')
s.text(30,116,'Через USB плати',3);s.text(30,107,'Без 230 В у корпусі',3);s.text(30,98,'Не подавати 2 джерела',3)
s.text(166,108,'GPIO32 ↔ кнопка ↔ GND',3);s.text(166,99,'INPUT_PULLUP; debounce',3);s.line(204,126,204,168,'ELECTRIC')
s.text(315,116,'GPIO33: START',3);s.text(315,108,'GPIO25: MODE',3);s.text(315,100,'GPIO13: зумер через NPN',3);s.line(310,145,235,145,'ELECTRIC');s.line(235,145,235,168,'ELECTRIC');s.line(350,136,350,145,'ELECTRIC');s.line(350,145,310,145,'ELECTRIC')
s.notes(['Це схема підключень модулів, не розведення друкованої плати.','SDA/SCL: підтяжки 4,7 кОм до 3,3 В, якщо їх немає на адаптері. Спільна земля.','TFT: перевірити плату живлення і підсвітку. Входи ESP32 не толерантні до 5 В.','*100 Гц - проєктна частота. Цокольовку SDP810 звірити за паспортом виробника.'],y=72);s.save()
s=Sheet(5,'Кнопковий макет і складання')
s.rect(35,172,45,35);s.circle(57.5,189.5,6);s.dim(35,172,80,172,-10);s.dim(80,172,80,207,10);s.text(35,220,'IL06 Макет натискання',3.5)
s.rect(35,121,45,20);s.line(38,121,38,138);s.line(77,121,77,138);s.line(38,138,77,138);s.dim(80,121,80,141,10)
s.text(119,224,'Порядок складання',4,bold=True)
for i,t in enumerate(['1. Надрукувати сухий корпус і перевірити отвори.','2. Поставити плати на ізолювальні стійки.','3. Підключити I²C, SPI та кнопку за IL-04.','4. Зібрати касету, підключити P+ до входу, P− до виходу.','5. Перевірити герметичність і нульовий сигнал.','6. Відкалібрувати касету з трубками та фільтрами.','7. Перевірити помилки датчика, насичення й кнопку.']):s.text(119,211-i*10,t,3.2)
s.notes(['Макет кнопки 45 × 35 × 20 мм; верхня стінка 3 мм; отвір Ø12.','Корпус кнопки відкритий знизу для стенда. Кришку розробити після вибору кнопки.','Для демонстрації використовувати контрольований потік повітря, а не ліки.','CAD містить STEP і STL. Деталі не перевірені друком або фізичним складанням.'],y=85)
s.save();pdf.save()
# Render CAD pdf preview pages
import fitz
p=fitz.open(CAD/'InhaleLab_Drawings_A3.pdf')
for i,page in enumerate(p):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(AS/f'drawing_{i+1}.png')
validation={'units':'mm','stage':'unbuilt engineering concept','solids_valid':all(o.val().isValid() for o in models.values()),'cad_parts':list(models),'drawing_sheets':5}
for f in CAD.glob('IL-0*.dxf'):
 d=ezdxf.readfile(f);a=d.audit();assert not a.has_errors
validation['dxf_audit']='5 files; no structural errors';(ROOT/'qa/cad_validation.json').write_text(json.dumps(validation,indent=2))
print(json.dumps(validation))
