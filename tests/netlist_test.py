from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'hardware/netlist.json').read_text());C={r['ref']:r for r in rows}
def pin(ref,name):return next(n for _,p,n in C[ref]['pins'] if p==name)
assert pin('U1','IO23')=='NASAL_EXCITE';assert pin('U1','VP')=='BAT_ADC';assert pin('U1','VN')=='MODULE_ID'
assert pin('U2','VDD')=='3V3';assert pin('U3','VCC')=='3V3'
assert pin('U4','CELL-')=='CELL_MINUS' and pin('U4','PROTECTED-')=='GND'
assert C['R3']['pins'][0][2]=='BOOST_IN';assert C['R6']['pins'][0][2]=='NASAL_EXCITE'
assert pin('Q1','C')=='BUZZ_LOW' and pin('D3','K')=='DEV_5V'
assert C['TH1']['value'].startswith('BR11KA104N')
for row in rows:
 nums=[p[0] for p in row['pins']];assert len(nums)==len(set(nums)),row['ref']
print('PASS: GPIO mapping, logic voltage, protected ground, switched battery divider, nasal excitation, buzzer clamp, unique module pins. This is NOT full ERC/DRC or an electrical test.')
