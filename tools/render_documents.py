from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
import re,html,json,fitz,csv
R=Path(__file__).resolve().parents[1]
for name,file in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf'),('DVM','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DVB',italic='DV',boldItalic='DVB')
S=getSampleStyleSheet()
S.add(ParagraphStyle('BodyUA',fontName='DV',fontSize=10,leading=15,spaceAfter=9,textColor=HexColor('#263b55'),splitLongWords=True))
S.add(ParagraphStyle('H1UA',fontName='DVB',fontSize=24,leading=30,spaceAfter=20,textColor=HexColor('#142443')))
S.add(ParagraphStyle('H2UA',fontName='DVB',fontSize=14,leading=19,spaceBefore=14,spaceAfter=9,textColor=HexColor('#008d96')))
S.add(ParagraphStyle('Cell',parent=S['BodyUA'],fontSize=8,leading=11,spaceAfter=0))
S.add(ParagraphStyle('CodeUA',fontName='DVM',fontSize=8,leading=11,spaceAfter=8,backColor=HexColor('#edf3f8'),splitLongWords=True))
def inline(t):
 t=html.escape(t);t=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t);t=re.sub(r'`([^`]+)`',r'<font name="DVM">\1</font>',t);return t
story=[]
cover='ASTHMABOT 2.0'
story+=[Spacer(1,28),Paragraph('ІНЖЕНЕРНЕ ДОСЬЄ · 22.11.2026',S['H2UA']),Paragraph(cover,S['H1UA']),Paragraph('ESP32 · PEF · модульна конструкція · відкритий код',S['BodyUA']),Image(str(R/'assets/assembly.png'),width=490,height=337),Paragraph('Володимир Булавин · КПІ · ПБ-62',S['H2UA']),Paragraph('Лабораторний прототип. Фізичних та клінічних випробувань немає. Усі зображення приладу — візуалізації CAD.',S['BodyUA']),PageBreak()]
order=['audit','concept','pef_feasibility','electronics','budget','mechanics','assembly','firmware','profiles','calibration','risks_and_standards','test_plan','limitations','analogues','demo_day','github_handoff','sources']
for file in order:
 p=R/'docs'/f'{file}.md'
 if not p.exists():continue
 lines=p.read_text().splitlines();i=0;code=False
 while i<len(lines):
  line=lines[i].strip();i+=1
  if not line:continue
  if line.startswith('```'):code=not code;continue
  if code:story.append(Paragraph(html.escape(line),S['CodeUA']));continue
  if line.startswith('|'):
   rows=[line]
   while i<len(lines) and lines[i].strip().startswith('|'):rows.append(lines[i].strip());i+=1
   cells=[]
   for row in rows:
    if re.fullmatch(r'[|:\- ]+',row):continue
    cells.append([Paragraph(inline(t.strip()),S['Cell']) for t in row.strip('|').split('|')])
   widths=[490/len(cells[0])]*len(cells[0]);table=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#d9f1f2')),('FONTNAME',(0,0),(-1,0),'DVB'),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.35,HexColor('#d5e0eb'))]));story.extend([table,Spacer(1,12)]);continue
  if line.startswith('# '):story.append(Paragraph(inline(line[2:]),S['H1UA']))
  elif line.startswith('## '):story.append(Paragraph(inline(line[3:]),S['H2UA']))
  else:
   while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','- ')):line+=' '+lines[i].strip();i+=1
   story.append(Paragraph(inline(line),S['BodyUA']))
 story.append(PageBreak())
# Full BOM presented with all prices/status, source labels URL stored in CSV and sources.
story.append(Paragraph('BOM · повна специфікація',S['H1UA']))
for row in csv.DictReader((R/'hardware/BOM.csv').open(encoding='utf-8-sig')):
 story.append(Paragraph(inline(row['Reference']+' · '+row['Component']),S['H2UA']))
 story.append(Paragraph(inline(f"Кількість: {row['Quantity']}. Ціна за одиницю: {row['Unit price']} {row['Currency']}. {row['Price status']}."),S['BodyUA']))
 story.append(Paragraph(inline('Альтернатива: '+row['Alternative']),S['BodyUA']))
 story.append(Paragraph(html.escape(row['Source URL']),S['Cell']))
def footer(c,doc):
 c.setStrokeColor(HexColor('#00aeb5'));c.line(48,40,547,40);c.setFont('DV',8);c.setFillColor(HexColor('#52657a'));c.drawString(48,27,'ASTHMABOT 2.0 · LAB · НЕ СЕРТИФІКОВАНО');c.drawRightString(547,27,str(doc.page))
SimpleDocTemplate(str(R/'docs/AsthmaBot2_Engineering.pdf'),pagesize=(595.28,841.89),leftMargin=50,rightMargin=50,topMargin=48,bottomMargin=55,title='AsthmaBot 2.0 — інженерне досьє',author='AsthmaBot project').build(story,onFirstPage=footer,onLaterPages=footer)
# Native deck renders → presentation PDF; preserves exact reviewed layout.
paths=list((R/'presentation/preview').glob('slide-*.png'))
paths.sort(key=lambda p:int(re.search(r'slide-(\d+)',p.name).group(1)))
out=fitz.open()
for p in paths:
 page=out.new_page(width=1280,height=720);page.insert_image(page.rect,filename=str(p))
out.save(R/'presentation/AsthmaBot2_DemoDay.pdf');print('Engineering PDF pages:',len(fitz.open(R/'docs/AsthmaBot2_Engineering.pdf')),'slides:',len(out))
