"""Share opaque original CGs between story and gallery, retaining the higher-quality copy."""
from pathlib import Path
import re,io,json,shutil
import numpy as np
from PIL import Image
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';B=R/'reports/before-v016';a=json.loads((O/'assets.txt').read_text('utf8'));m=json.loads(re.search(r'const assets=(.*);',(B/'src/common/assets.js').read_text('utf8')).group(1));mpk=MPK('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR/bg.mpk');rows=[]
for key,old in list(m.items()):
    if not key.startswith('bg') or not key[2:].isdigit():continue
    ident=key[2:];other='gal'+ident
    if other not in m or a['backgroundGeometry'][ident]['transparent'] or m[other]==old:continue
    master=Image.open(io.BytesIO(mpk.read(int(ident)))).convert('RGBA');assert master.getchannel('A').getextrema()==(255,255);master.thumbnail((320,180),Image.Resampling.LANCZOS)
    original=O/'img'/old;backup=B/'src/common/img'/old;prior=Image.open(original if original.exists() else backup).convert('RGB');target=Image.open(O/'img'/m[other]).convert('RGB');assert target.size==prior.size==master.size
    ref=np.asarray(master.convert('RGB'),dtype='float32');before=float(np.mean((ref-np.asarray(prior,dtype='float32'))**2));after=float(np.mean((ref-np.asarray(target,dtype='float32'))**2));assert after<=before,(key,before,after)
    rows.append({'key':key,'galleryKey':other,'from':old,'to':m[other],'sourceArchiveId':int(ident),'sourceName':mpk.by_id[int(ident)]['name'],'oldMse':before,'newMse':after,'dimensions':list(target.size)});m[key]=m[other]
used=set(m.values());removed=[]
for row in rows:
    old=row['from']
    if old in used or old in removed:continue
    p=(O/'img'/old).resolve();assert p.is_relative_to((O/'img').resolve());backup=B/'src/common/img'/old;backup.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():shutil.move(str(p),str(backup))
    removed.append(old)
(O/'assets.js').write_text('const assets='+json.dumps(m,separators=(',',':'))+";\nexport function imagePath(key){return assets[key]?'/common/img/'+assets[key]:'/common/black.png';}\n",encoding='utf8')
report={'result':'passed','sameOpaqueOriginalArchiveEntry':True,'dimensionsAndCompositionUnchanged':True,'allSourceRelativeMseImproved':True,'reusedCGs':len(rows),'removedFiles':len(removed),'removedBytes':sum((B/'src/common/img'/name).stat().st_size for name in removed),'meanOldMse':sum(x['oldMse'] for x in rows)/len(rows),'meanNewMse':sum(x['newMse'] for x in rows)/len(rows),'rows':rows}
(R/'reports/cg-reuse-v016.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))
