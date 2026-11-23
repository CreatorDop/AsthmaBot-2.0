from pathlib import Path
import cadquery as cq,ezdxf,fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1];D=R/'cad';mm=72/25.4
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
c=canvas.Canvas(str(D/'AB20_00_assembly.pdf'),pagesize=(420*mm,297*mm));c.scale(mm,mm);doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace();doc.styles.new('UA',dxfattribs={'font':'DejaVuSans.ttf'})
def line(x,y,xx,yy):m.add_line((x,y),(xx,yy));c.setLineWidth(.2);c.line(x,y,xx,yy)
def text(x,y,t,size=3):m.add_text(t,dxfattribs={'insert':(x,y),'height':size,'style':'UA'});c.setFont('DV',size);c.drawString(x,y,t)
def rect(x,y,w,h):
 for a,b,cc,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,cc,d)
rect(10,10,400,277);text(18,277,'ASTHMABOT 2.0 / СКЛАДАЛЬНЕ КРЕСЛЕННЯ',5)
text(18,268,'Масштаб1:1 · мм · робочий ескіз стенда · компоненти показано габаритами',3)
# Габаритна компоновка у відкритому корпусі.
rect(25,160,124,80);rect(149,182,11,30)
for x,y,w,h,label in [(8,10,48.26,27.94,'ESP32'),(83,48,29,18,'SDP810'),(70,8,37,17,'BOOST'),(75,28,28,17.5,'TP4056')]:rect(25+x,160+y,w,h);text(27+x,166+y,label,2.5)
rect(33,211.75,65.5,18.5);text(38,220,'18650 / ремінь',3)
# OLED на кришці: пунктиром позначаємо проєкцію, корпус і плати не свердлити за цим прямокутником.
m.add_lwpolyline([(43,174),(70.5,174),(70.5,201.7),(43,201.7),(43,174)],dxfattribs={'linetype':'Continuous'});c.setDash(2,2);c.rect(43,174,27.5,27.7);c.setDash();text(44,204,'OLED на кришці',2.4)
for r in [30,24,20,16]:m.add_circle((197,200),r);c.circle(197,200,r,stroke=1,fill=0)
text(167,240,'PeakFlow / фланецьØ60',3);text(25,250,'Вигляд зверху / кришку умовно знято',3)
rect(25,83,124,44);rect(173,83,48,80);line(167,123,227,123);text(25,72,'Вигляд спереду / основні габарити',3)
for x,y in [(31,166),(143,166),(31,234),(143,234)]:m.add_circle((x,y),1.25);c.circle(x,y,1.25)
for y in [105,112]:line(149,y,168,y);line(168,y,168,113 if y==105 else 133);line(168,113 if y==105 else 133,173,113 if y==105 else 133)
text(156,65,'Два відводи тиску; шланги схематично',2.5)
for p1,p2,base,angle in [((25,160),(149,160),(25,150),0),((25,160),(25,240),(15,160),90),((25,83),(25,127),(15,83),90),((173,83),(173,163),(235,83),90)]:m.add_linear_dim(base=base,p1=p1,p2=p2,angle=angle,override={'dimtxt':2.5,'dimasz':2,'dimdec':1}).render()
text(68,151,'124',3);text(13,196,'80',3);text(13,104,'44',3);text(230,123,'80',3)
text(268,246,'Склад вузлів',4)
items=['01 Основа корпусу','02 Кришка','03 Носій на ключовій рейці','04 Вхідна половина каналу','05 Вихідна половина каналу','06 ДіафрагмаØ32','07 AirFlow Basic (окремо)','08 Змінний мундштук','09 Затискач каналу','10–11 NasalTrack (окремо)','12 Штовхач кнопки ×3','13 Притискна планка','Електроніка — за BOM.csv']
for i,t in enumerate(items):text(268,232-i*9,t,3)
text(268,103,'Примітки',4)
for i,t in enumerate(['4×M3 — кришка; фланці4×M3.','M3 через рейку/носій/затискач.','Трубки: P+ до діафрагми, P− після.','Плати — на ізольованих ложементах.','Пробне складання обов’язкове.','Без людських проб до перевірки.']):text(268,92-i*7,t,2.6)
rect(210,10,200,30);text(216,30,'AB20-00 / REV2.0-LAB / 22.11.2026',3);text(216,22,'Булавин Володимир · КПІ · ПБ-62',3);text(216,14,'Креслення не засвідчує медичну відповідність',2.7)
c.showPage();c.save();doc.saveas(D/'AB20_00_assembly.dxf')
combined=fitz.open()
for p in ['AB20_00_assembly.pdf','AsthmaBot2_drawings_A3.pdf']:combined.insert_pdf(fitz.open(D/p))
combined.save(D/'AsthmaBot2_CAD_set.pdf');print('Assembly DXF/PDF and 14-page drawing set generated')
