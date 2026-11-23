"""Обмежена локальна перевірка відомих форматів секретів; не гарантія їх відсутності."""
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1]
patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{35,}'),re.compile(r'sk-[A-Za-z0-9_-]{30,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'AKIA[0-9A-Z]{16}')]
ignore={'.git','.pio','node_modules','video_frames','video_composed','__pycache__'};found=[];checked=0
for p in R.rglob('*'):
 if not p.is_file() or any(t in ignore for t in p.relative_to(R).parts) or p.suffix.lower() not in {'.cpp','.h','.js','.mjs','.py','.json','.md','.yml','.yaml','.ini','.txt','.csv','.html','.css','.log'}:continue
 if p.name=='check_secrets.py':continue
 s=p.read_text(errors='replace');checked+=1
 if any(rx.search(s) for rx in patterns):found.append(str(p.relative_to(R)))
print(f'Scanned {checked} text files for known token/private-key formats. Matches: {len(found)}.')
for p in found:print('Review file:',p)
sys.exit(bool(found))
