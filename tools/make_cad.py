"""Параметричний механічний прототип. Міліметри; верифікація на стенді обов'язкова."""
from pathlib import Path
import cadquery as cq
import json,math,ezdxf
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def bounds(shape):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(shape.wrapped,b,False,False);return cq.BoundBox(b)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1];D=R/'cad';D.mkdir(exist_ok=True)
def box(w,d,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,d,h,centered=(False,False,False)).translate((x,y,z))
def cylinder(r,h,x=0,y=0,z=0):return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))
def rounded(w,d,h,r):return cq.Workplane('XY').box(w,d,h,centered=(False,False,False)).edges('|Z').fillet(r)
parts={};placements={}
def add(name,obj,loc=(0,0,0),color=(.1,.75,.8)):
 assert obj.val().isValid(),name
 parts[name]=obj;placements[name]={'xyz':loc,'color':color}
 cq.exporters.export(obj,str(D/(name+'.step')));cq.exporters.export(obj,str(D/(name+'.stl')),tolerance=.08,angularTolerance=.15)
# Корпус: внутрішні ложементи мають зазори, а не вигадані монтажні отвори плат.
base=rounded(124,80,41.5,5).cut(rounded(119,75,42,3).translate((2.5,2.5,2.5)))
for x,y in [(6,6),(118,6),(6,74),(118,74)]:
 base=base.union(cylinder(3.7,38.5,x,y,2.5)).cut(cylinder(1.25,16,x,y,26))
# Полиці ESP32 та ремінь: розміри V4 48.26 x 27.94, плата z=7.
for y in [7,35.94]:
 base=base.union(box(51,2,4.5,7,y,2.5))
for x in [5.5,57.26]:base=base.union(box(2,29.94,2,x,8,7))
# Сідла батареї Ø18.5, довжина65.3: утримання ременем, не жорстким затиском.
for x in [12,63]:
 saddle=box(5,24,12,x,49,2.5)
 cutter=cq.Workplane('YZ').center(61,14.5).circle(9.8).extrude(7).translate((x-1,0,0))
 base=base.union(saddle.cut(cutter))
for x,y,w,d in [(82,47,31,20),(74,27,30,19.5),(69,7,39,19)]:
 for yy in [y,y+d-1.5]:base=base.union(box(w,1.5,2.5,x,yy,2.5))
# Виходи джгутів; USB плати тільки для прошивання, доступ зліва.
base=base.cut(box(5,13,10,-1,15,7))
base=base.cut(box(5,18,10,121,48,28))
# Кабель зовнішнього USB-C заряджання в пазі: роз'єм на проводі, розмір плати не припускається.
base=base.cut(box(10,5,6,77,-1,12))
# Ключовий механічний інтерфейс: зовнішня асиметрична рейка, відкритий верх.
rail=box(5,26,34,124,24,5).union(box(3,30,34,129,22,5)).union(box(8,30,3,124,22,2))
rail=rail.union(box(3,3,30,132,22,5)) # асиметричний ключ
base=base.union(rail).cut(cq.Workplane('YZ').center(40,21).circle(1.7).extrude(15).translate((122,0,0)))
add('AB20_01_base',base)
lid=rounded(124,80,2.5,5)
for x,y in [(6,6),(118,6),(6,74),(118,74)]:lid=lid.cut(cylinder(1.7,4,x,y,-.5))
lid=lid.cut(box(28.1,28.3,4,17.7,13.7,-.5))
for x,y in [(55,23),(55,35),(55,47)]:lid=lid.cut(cylinder(3.2,4,x,y,-.5))
for x,y,r in [(71,19,1.6),(71,28,1.6),(108,33,3.1)]:lid=lid.cut(cylinder(r,4,x,y,-.5))
# Приховані полиці під OLED: притиск окремими планками / знімною стрічкою.
for x in [14.5,46]:lid=lid.union(box(3,32,4,x,12,-4))
add('AB20_02_lid',lid,(0,0,41.5),(.76,.87,.91))
# Накладка насадки: кишеня на рейку із зазором .4 та отвором під гвинт стопора.
carrier=box(13,38,40).cut(box(8.8,30.8,41,-.4,3.6,3)).cut(box(3.8,3.8,41,8.4,3.6,3))
# Поперечний отвір під притиск M3, різьба нарізається / вставна гайка після перевірки.
carrier=carrier.cut(cq.Workplane('YZ').center(21.6,19).circle(1.7).extrude(15))
add('AB20_03_module_carrier',carrier,(124,18.4,2),(.65,.39,.95))
# Канал уздовж Z, діафрагма між двома фланцями. Отвори тиску під вклеювані трубки OD3.
def channel_half(length,tap_z,flange_at):
 b=cylinder(24,length).cut(cylinder(20,length+2,z=-1))
 fl=cylinder(30,4,z=flange_at).cut(cylinder(20,6,z=flange_at-1))
 b=b.union(fl)
 for a in [45,135,225,315]:
  x,y=26*math.cos(math.radians(a)),26*math.sin(math.radians(a));b=b.cut(cylinder(1.7,6,x,y,flange_at-1))
 # Радіальний тиск: вісь X; зовнішній діаметр трубки3.0, свердло3.1.
 b=b.cut(cq.Workplane('YZ').center(0,tap_z).circle(1.55).extrude(30))
 return b
up=channel_half(40,30,36);down=channel_half(40,10,0)
# Посадка діафрагми: глибина1.2 з кожного боку; сумарно2.4 (діафрагма2 + прокладки).
up=up.cut(cylinder(22.2,1.2,z=38.8));down=down.cut(cylinder(22.2,1.2))
add('AB20_04_peak_inlet',up,(172,40,0),(.08,.69,.75))
add('AB20_05_peak_outlet',down,(172,40,40),(.08,.69,.75))
disc=cylinder(22,2).cut(cylinder(16,4,z=-1));add('AB20_06_diaphragm_D32',disc,(172,40,39),(.96,.66,.13))
basic=cylinder(24,80).cut(cylinder(20,82,z=-1));add('AB20_07_airflow_basic',basic,(235,40,0),(.25,.81,.67))
# Мундштук-демонстратор з повним просвітом40, сполучення ковзне, не стандартний медичний конус.
mouth=cylinder(25.5,18).cut(cylinder(24.3,13,z=-.1)).cut(cylinder(20,20,z=-1))
mouth=mouth.rotate((0,0,0),(1,0,0),180).translate((0,0,13))
add('AB20_08_mouthpiece',mouth,(172,40,0),(.75,.9,.95))
# Затискач каналу та перемичка до універсального носія — стендова збірка.
clamp=cylinder(27,8).cut(cylinder(24.3,10,z=-1)).cut(box(6,30,10,-3,0,-1)).union(box(11,10,8,-35,-5,0))
clamp=clamp.cut(cq.Workplane('YZ').center(0,4).circle(1.7).extrude(13).translate((-36,0,0)))
clamp=clamp.cut(cq.Workplane('YZ').center(0,4).circle(1.25).extrude(30))
add('AB20_09_channel_clamp',clamp,(172,40,17),(.65,.39,.95))
# NasalTrack: окремий експериментальний зонд BR11 Ø0.30; отвір під власний ізоляційний тримач.
nasal=box(34,22,14).cut(box(29,17,12,2.5,2.5,2.5)).union(box(6,6,18,14,8,14))
nasal=nasal.cut(cylinder(1.4,22,17,11,12))
add('AB20_10_nasal_pod',nasal,(220,85,0),(.65,.39,.95))
cap=box(34,22,2).cut(cylinder(3.5,4,17,11,-1));add('AB20_11_nasal_lid',cap,(220,85,14),(.76,.87,.91))
# Окрема кнопка для пружної мембрани/плати тактових кнопок. Довжину підганяють під реальний SKU.
plunger=cylinder(3,6).union(cylinder(4,1));add('AB20_12_button',plunger,(55,23,39),(.96,.66,.13))
# Стяжні петлі універсальні — не заявляємо точні отвори для невідомих модулів.
strap=box(55,4,2)
for x in [3,52]:strap=strap.cut(cylinder(1.7,4,x,2,-1))
add('AB20_13_retaining_strip',strap,(7,7,9),(.76,.87,.91))
assembly=cq.Assembly(name='AsthmaBot2_LAB')
for name,obj in parts.items():assembly.add(obj,name=name,loc=cq.Location(cq.Vector(*placements[name]['xyz'])),color=cq.Color(*placements[name]['color']))
assembly.save(str(D/'AsthmaBot2_assembly.step'))
# Реальні габарити комплектуючих; окремий файл, бо це НЕ модель внутрішньої електроніки.
env={'ESP32_DevKitC_V4':(48.26,27.94,18,8,10,7),'SDP810_500Pa':(29,18,27.05,83,48,5),'OLED_SBC_OLED01':(27.5,27.7,11.2,18,14,28.8),'MT3608_RCS123033':(37,17,14,70,8,5),'TP4056_myproject':(28,17.5,4,75,28,5)}
# ESP32 висота18 — монтажний резерв; решта з джерел у docs/mechanics.md.
A=cq.Assembly(name='Component_envelopes_NOT_vendor_models')
for k,(w,d,h,x,y,z) in env.items():A.add(box(w,d,h,x,y,z),name=k)
bat=cq.Workplane('YZ').center(61,14.5).circle(9.25).extrude(65.3).translate((8,0,0));A.add(bat,name='NCR18650B')
A.save(str(D/'component_envelopes.step'))
manifest=[]
for k,obj in parts.items():
 bb=bounds(obj.val());manifest.append({'part':k,'valid':obj.val().isValid(),'volume_mm3':round(obj.val().Volume(),3),'bounds_mm':[round(v,3) for v in [bb.xlen,bb.ylen,bb.zlen]],**placements[k]})
(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
# CAD-похідні контури: ортогональні види з геометрії, а не намальовані прямокутники.
import re
from xml.etree import ElementTree as ET
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
MM=72/25.4;pdf=canvas.Canvas(str(D/'AsthmaBot2_drawings_A3.pdf'),pagesize=(420*MM,297*MM))
def drawing(name,obj,index):
 doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace();doc.styles.new('UA',dxfattribs={'font':'DejaVuSans.ttf'})
 pdf.saveState();pdf.scale(MM,MM)
 def line(x,y,xx,yy):m.add_line((x,y),(xx,yy));pdf.setLineWidth(.2);pdf.line(x,y,xx,yy)
 def txt(x,y,s,h=3):m.add_text(s,dxfattribs={'height':h,'style':'UA','insert':(x,y)});pdf.setFont('DV',h);pdf.drawString(x,y,s)
 def rect(x,y,w,h):
  for a,b,c,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,c,d)
 rect(10,10,400,277);txt(18,277,'ASTHMABOT 2.0 / РОБОЧИЙ ЕСКІЗ ДЛЯ СТЕНДА',5)
 txt(18,267,name,4);txt(18,259,'Масштаб 1:1. Одиниці мм. Посадки перевірити пробним друком.',3)
 # exact tessellated outlines projected; visible+hidden projection may include back edges.
 for label,origin,axes in [('Зверху',(35,140),(0,1)),('Спереду',(35,70),(0,2)),('Збоку',(220,140),(1,2))]:
  txt(origin[0],origin[1]-10,label)
  for edge in obj.val().Edges():
   pts=edge.discretize(Deflection=.15) if hasattr(edge,'discretize') else None
   # CadQuery Edge.sample supplies exact BREP samples.
   if pts is None:
    pts,_=edge.sample(30)
   for a,b in zip(pts,pts[1:]):
    aa=a.toTuple();bb=b.toTuple();line(origin[0]+aa[axes[0]],origin[1]+aa[axes[1]],origin[0]+bb[axes[0]],origin[1]+bb[axes[1]])
 bb=bounds(obj.val())
 dim=m.add_linear_dim(base=(35,130),p1=(35+bb.xmin,140+bb.ymin),p2=(35+bb.xmax,140+bb.ymin),angle=0,override={'dimtxt':2.5,'dimasz':2,'dimdec':2});dim.render()
 line(35+bb.xmin,135,35+bb.xmax,135);line(35+bb.xmin,132,35+bb.xmin,139);line(35+bb.xmax,132,35+bb.xmax,139);txt(35+bb.xmin+bb.xlen/2,136,f'{bb.xlen:.2f}',2.5)
 txt(210,80,f'Габарит: {bb.xlen:.2f} × {bb.ylen:.2f} × {bb.zlen:.2f} мм')
 if 'base' in name:txt(210,68,'Стінка 2.5; основа 2.5; 4 отв. Ø2.5');txt(210,60,'Центри: (6;6), (118;6), (6;74), (118;74)')
 elif 'peak' in name:txt(210,68,'Канал Ø40; оболонка Ø48; фланець Ø60');txt(210,60,'4 отв. Ø3.4 на Ø52; відбір тиску Ø3.1')
 elif 'diaphragm' in name:txt(210,68,'Отвір Ø32; зовнішній Ø44; товщина 2')
 elif 'lid' in name:txt(210,68,'Позиції вирізів — у параметричному джерелі')
 rect(210,10,200,32);txt(216,32,f'AB20 / {index:02d} / REV 2.0-LAB / 22.11.2026');txt(216,24,'Булавин Володимир · КПІ · ПБ-62');txt(216,16,'Не для контакту з людиною без перевірки матеріалів',2.7)
 pdf.restoreState();pdf.showPage();doc.saveas(D/(name+'.dxf'))
for i,(name,obj) in enumerate(parts.items(),1):drawing(name,obj,i)
pdf.save();print('CAD:',len(parts),'parts, STEP/STL/DXF and A3 PDF')
