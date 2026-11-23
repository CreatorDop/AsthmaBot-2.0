from pathlib import Path
import uuid,json,csv
R=Path(__file__).resolve().parents[1];H=R/'hardware'
def uid():return str(uuid.uuid4())
def quote(s):return '"'+str(s).replace('\\','\\\\').replace('"','\\"')+'"'
# Поля: позначення, значення, координати, контакти (номер, ім’я, електрична мережа).
comps=[]
def add(ref,value,x,y,pins):comps.append(dict(ref=ref,value=value,x=x,y=y,pins=pins))
j2=['3V3','EN','VP','VN','IO34','IO35','IO32','IO33','IO25','IO26','IO27','IO14','IO12','GND','IO13','D2','D3','CMD','5V'];j3=['GND','IO23','IO22','TX','RX','IO21','GND','IO19','IO18','IO5','IO17','IO16','IO4','IO0','IO2','IO15','D1','D0','CLK']
nets={'3V3':'3V3','VP':'BAT_ADC','VN':'MODULE_ID','IO23':'NASAL_EXCITE','IO34':'NASAL_ADC','IO32':'BTN_NEXT','IO33':'BTN_OK','IO25':'BTN_BACK','IO26':'LED_OK_CTRL','IO27':'LED_ERR_CTRL','IO13':'BUZZ_CTRL','5V':'DEV_5V','GND':'GND','IO22':'SENSOR_SCL','IO21':'SENSOR_SDA','IO19':'OLED_SCL','IO18':'OLED_SDA'}
add('U1','ESP32-DevKitC V4 / WROOM-32E',80,100,[(f'J2.{i+1}',n,nets.get(n)) for i,n in enumerate(j2)]+[(f'J3.{i+1}',n,nets.get(n)) for i,n in enumerate(j3)])
add('U2','SDP810-500Pa / 0x25',215,40,[('1','SCL','SENSOR_SCL'),('2','VDD','3V3'),('3','GND','GND'),('4','SDA','SENSOR_SDA')])
add('U3','SBC-OLED01 SSD1306 / 0x3C',350,40,[('GND','GND','GND'),('VCC','VCC','3V3'),('SCL','SCL','OLED_SCL'),('SDA','SDA','OLED_SDA')])
for ref,val,x,y,na,nb in [('R1','4.7k 1%',200,82,'3V3','SENSOR_SCL'),('R2','4.7k 1%',200,112,'3V3','SENSOR_SDA'),('C1','100nF X7R',200,142,'3V3','GND'),('R3','100k 1%',335,82,'BOOST_IN','BAT_ADC'),('R4','100k 1%',335,112,'BAT_ADC','GND'),('C2','100nF X7R',335,142,'BAT_ADC','GND'),('R5','10k 1%',470,40,'3V3','MODULE_ID'),('R6','100k 1%',470,70,'NASAL_EXCITE','NASAL_ADC')]:add(ref,val,x,y,[('1','1',na),('2','2',nb)])
add('C5','10nF X7R',335,185,[('1','1','NASAL_ADC'),('2','2','GND')])
add('J1','Keyed 3-pin module connector',470,112,[('1','ID','MODULE_ID'),('2','GND','GND'),('3','NTC','NASAL_ADC')])
add('RM1','Module ID: Basic 1k / Peak 4.7k / Nasal 10k',470,158,[('1','ID','MODULE_ID'),('2','GND','GND')])
add('TH1','BR11KA104N 100k / Nasal only',470,198,[('1','NTC','NASAL_ADC'),('2','GND','GND')])
for i,net in enumerate(['BTN_NEXT','BTN_OK','BTN_BACK']):add('SW'+str(i+2),'Momentary NO / pullup in ESP32',60+i*140,225,[('1','1',net),('2','2','GND')])
for ref,val,x,y,na,nb in [('R7','1k',60,270,'LED_OK_CTRL','LED_OK_A'),('D1','Green LED 3mm',60,310,'LED_OK_A','GND'),('R8','1k',200,270,'LED_ERR_CTRL','LED_ERR_A'),('D2','Red LED 3mm',200,310,'LED_ERR_A','GND'),('R9','2.2k',335,270,'BUZZ_CTRL','Q_BASE'),('R10','100k',335,310,'Q_BASE','GND')]:add(ref,val,x,y,[('1','A/1',na),('2','K/2',nb)])
add('Q1','2N3904 TO92: verify E-B-C vendor',470,265,[('1','E','GND'),('2','B','Q_BASE'),('3','C','BUZZ_LOW')])
add('BZ1','Active buzzer 5V <=20mA',470,310,[('1','+','DEV_5V'),('2','-','BUZZ_LOW')])
add('D3','1N4148 flyback',470,350,[('1','A','BUZZ_LOW'),('2','K','DEV_5V')])
# Окремий аркуш живлення, ті самі глобальні мережі. Формуємо також CSV усіх контактів.
power=[]
old=comps;comps=power
add('BT1','NCR18650B 1S / factory tabs',60,50,[('+','+','CELL_PLUS'),('-','-','CELL_MINUS')])
add('F1','PTC 1A hold / >=6V',60,100,[('1','1','CELL_PLUS'),('2','2','BATT_FUSED')])
add('U4','TP4056 + DW01A + FS8205A module',200,65,[('IN+','5V_IN','CHARGE_5V'),('IN-','INPUT_GND','GND'),('B+','CELL+','BATT_FUSED'),('B-','CELL-','CELL_MINUS'),('OUT+','PROTECTED+','PACK_PLUS'),('OUT-','PROTECTED-','GND')])
add('J2','USB-C 5V breakout: sink CC resistors fitted',60,170,[('VBUS','5V','USB_CHG_5V'),('GND','GND','GND')])
add('SW1','DPDT ON-ON / CHARGE-RUN (linked poles)',200,180,[('1','A-common','USB_CHG_5V'),('2','A-CHARGE','CHARGE_5V'),('3','A-RUN',None),('4','B-common','PACK_PLUS'),('5','B-CHARGE',None),('6','B-RUN','BOOST_IN')])
add('U5','MT3608 module / set 5.00V BEFORE connecting',350,65,[('IN+','IN+','BOOST_IN'),('IN-','IN-','GND'),('OUT+','OUT+','BOOST_5V'),('OUT-','OUT-','GND')])
add('JP1','REMOVE for USB flashing / power interlock',350,145,[('1','BOOST','BOOST_5V'),('2','DEVKIT','DEV_5V')])
add('C3','220uF 10V low ESR',470,65,[('1','+','DEV_5V'),('2','-','GND')])
add('C4','100nF X7R',470,110,[('1','1','DEV_5V'),('2','2','GND')])
add('RPROG','4.7k / replace TP4056 onboard RPROG',350,215,[('1','TP4056 pin2 PROG','PROG_INTERNAL'),('2','TP4056 pin3 GND','GND')])
# RPROG is a replacement inside U4, explicitly connect external representation.
power[2]['pins'].append(('PROG','TP4056 pin2','PROG_INTERNAL'))
comps=old

def generate(items,path,title,notes):
 def e(tag,*args):return '('+tag+' '+ ' '.join(str(a) for a in args)+')'
 def at(x,y,angle=0):return e('at',f'{x:.4f}',f'{y:.4f}',angle)
 def effects(size=1.27,justify=None,hide=False):return e('effects',e('font',e('size',size,size)),e('justify',justify) if justify else '',e('hide','yes') if hide else '')
 def prop(name,value,x,y,size=1.27):return e('property',quote(name),quote(value),at(x,y),effects(size))
 rootid=uid();parts=[e('version',20250114),e('generator',quote('asthmabot2')),e('uuid',rootid),e('paper',quote('A2')),e('title_block',e('title',quote(title)),e('date',quote('2026-11-22')),e('rev',quote('2.0-LAB')),e('company',quote('KPI / AsthmaBot')))];libs=[];instances=[]
 for c in items:
  ref,val,x,y,pins=c['ref'],c['value'],c['x'],c['y'],c['pins'];name='AB:'+ref;half=(len(pins)+1)//2;h=max(8,(half-1)*2.54/2+5);width=27
  graphic=e('symbol',quote(ref+'_0_1'),e('rectangle',e('start',-width,h),e('end',width,-h),e('stroke',e('width',.254),e('type','default')),e('fill',e('type','background'))))
  pinsym=[];coords=[]
  for i,(number,label,net) in enumerate(pins):
   left=i<half;row=i if left else i-half;py=(half-1)*2.54/2-row*2.54;px=-(width+5.08) if left else width+5.08;angle=0 if left else 180
   pinsym.append(e('pin','passive','line',at(px,py,angle),e('length',5.08),e('name',quote(label),effects(1)),e('number',quote(number),effects(.9))))
   coords.append((number,x+px,y-py,net,left))
  libs.append(e('symbol',quote(name),e('pin_names',e('offset',.8)),e('in_bom','yes'),e('on_board','yes'),prop('Reference',ref,0,h+5),prop('Value',val,0,h+2),graphic,e('symbol',quote(ref+'_1_1'),*pinsym)))
  instances.append(e('symbol',e('lib_id',quote(name)),at(x,y),e('unit',1),e('in_bom','yes'),e('on_board','yes'),e('dnp','no'),e('uuid',uid()),prop('Reference',ref,x,y-h-6,1.5),prop('Value',val,x,y-h-3,1.1),*[e('pin',quote(p[0]),e('uuid',uid())) for p in pins],e('instances',e('project',quote(path.stem),e('path',quote('/'+rootid),e('reference',quote(ref)),e('unit',1))))))
  for num,px,py,net,left in coords:
   if net is None:instances.append(e('no_connect',e('at',px,py),e('uuid',uid())));continue
   ex=px+(-9 if left else 9)
   instances.append(e('wire',e('pts',e('xy',px,py),e('xy',ex,py)),e('stroke',e('width',0),e('type','default')),e('uuid',uid())))
   instances.append(e('label',quote(net),at(ex,py),effects(1,'right bottom' if left else 'left bottom'),e('uuid',uid())))
 parts.append(e('lib_symbols',*libs));parts.extend(instances)
 for i,n in enumerate(notes):parts.append(e('text',quote(n),at(35,370+i*7),effects(1.6,'left bottom'),e('uuid',uid())))
 path.write_text(e('kicad_sch',*parts))

generate(comps,H/'AsthmaBot2_logic.kicad_sch','ASTHMABOT 2.0 / LOGIC + SENSOR / LAB ONLY',[
 'R1/R2: fit only if sensor adapter has no pullups. OLED: onboard pullups to 3V3 only.',
 'U1 pin numbering is header.pin (J2 / J3), per Espressif DevKitC V4. Unused pins marked NC.',
 'J1: separate keyed connector. RM1 fitted inside each module; TH1 only in NasalTrack.',
 'GND = protected OUT-; never bypass protection by bonding CELL_MINUS to GND.'])
generate(power,H/'AsthmaBot2_power.kicad_sch','ASTHMABOT 2.0 / BATTERY + CHARGE / LAB ONLY',[
 'SW1 links both poles: CHARGE disconnects boost; RUN disconnects external USB charging input.',
 'Block module onboard USB socket; charge via J2 + SW1 only. RPROG replaced, not paralleled.',
 'Remove JP1 before connecting ESP32 USB. Do not provide two simultaneous DevKit power sources.',
 'Verify U4 variant/protection ICs, polarity, charger thermal behavior, and 5V before assembly.'])
with (H/'connections.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','Pin','Pin name','Net']);
 for c in comps+power:
  for num,name,net in c['pins']:w.writerow([c['ref'],c['value'],num,name,net or 'NC'])
(H/'netlist.json').write_text(json.dumps(comps+power,ensure_ascii=False,indent=2))
print('Schematic source and netlist written')
