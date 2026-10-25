from pathlib import Path
import json,shutil,io,re,hashlib
from PIL import Image
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';a=json.loads((O/'assets.txt').read_text('utf8'));flat=O/'images'
if not flat.exists():flat=R/'reports/master-images'
archive=MPK('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR/bg.mpk');byname={Path(x['name']).stem:x['id'] for x in archive.entries};groups={}
for row in archive.entries:
    name=Path(row['name']).stem;m=re.match(r'(SG0_EV\d+|EV_[A-Z]+\d+)',name)
    if m:groups.setdefault(m[1],[]).append(row['id'])
def full(ident,seen=None):
    seen=set() if seen is None else seen;assert ident not in seen;seen.add(ident);im=Image.open(io.BytesIO(archive.read(ident))).convert('RGBA')
    if im.getchannel('A').getextrema()[0]==255:return im
    name=Path(archive.by_id[ident]['name']).stem;group=re.match(r'(SG0_EV\d+|EV_[A-Z]+\d+)',name)[1]
    candidates=[byname.get(re.sub(r'\d+$','',name))] if re.search(r'[A-Z]\d+$',name) else []
    candidates+=groups[group]
    for parent in candidates:
        if parent is None or parent in seen:continue
        base=Image.open(io.BytesIO(archive.read(parent))).convert('RGBA')
        if parent==candidates[0] or base.getchannel('A').getextrema()[0]==255:
            base=full(parent,seen);base.alpha_composite(im);return base
    return im
gallery=[]
for group,ids in groups.items():
    variants=[]
    for i in ids:
        key='gal'+str(i);name=key+'.jpg';im=full(i);im.thumbnail((320,180),Image.Resampling.LANCZOS);im.convert('RGB').save(flat/name,quality=70,optimize=True);a['assets'][key]=name;variants.append(key)
    gallery.append({'image':variants[0],'images':variants,'label':group})
(O/'gallery.txt').write_text(json.dumps(gallery,separators=(',',':')),'utf8')
dest=O/'img';dest.mkdir(exist_ok=True);mapped={};unique={};rows=[]
for key,name in sorted(a['assets'].items()):
    data=(flat/name).read_bytes()
    if name.startswith('p') and name.endswith('.png'):
        im=Image.open(io.BytesIO(data)).convert('RGBA');buf=io.BytesIO();im.quantize(colors=64,method=Image.Quantize.FASTOCTREE).save(buf,format='PNG',optimize=True);data=buf.getvalue()
    digest=hashlib.sha256(data).hexdigest()
    if digest not in unique:
        index=len(unique);p=Path(str(index//40))/f'{index%40:02d}{Path(name).suffix}';target=dest/p;target.parent.mkdir(exist_ok=True);target.write_bytes(data);unique[digest]=p.as_posix();rows.append({'file':p.as_posix(),'bytes':len(data),'sha256':digest})
    mapped[key]=unique[digest]
(O/'assets.js').write_text('const assets='+json.dumps(mapped,separators=(',',':'))+";\nexport function imagePath(key){return assets[key]?'/common/img/'+assets[key]:'/common/black.png';}\n",'utf8')
source=(O/'images').resolve();backup=(R/'reports/master-images').resolve();workspace=R.resolve()
assert source.is_relative_to(workspace) and backup.is_relative_to(workspace)
if source.exists():
    assert not backup.exists(),'Generated master-image backup already exists';shutil.move(str(source),str(backup))
(R/'reports/final-images.json').write_text(json.dumps({'unique':len(unique),'bytes':sum(x['bytes'] for x in rows),'galleryGroups':len(gallery),'galleryVariants':sum(len(g['images']) for g in gallery),'maxFilesPerDirectory':40,'files':rows},indent=2),'utf8');print('FINAL_IMAGES',len(unique),sum(x['bytes'] for x in rows),len(gallery),'groups')
