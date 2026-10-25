"""Read original MPKs, retain composition geometry, export bounded watch images."""
from pathlib import Path
import io,struct,json,hashlib,re,os
from PIL import Image
from mpk import MPK
ROOT=Path(__file__).resolve().parents[1]
GAME=Path(os.environ.get('SG0_GAME_ROOT','G:/SteamLibrary/steamapps/common/STEINS;GATE 0'))/'USRDIR'
OUT=ROOT/'src/common';DEST=OUT/'images';DEST.mkdir(parents=True,exist_ok=True)
REPORT=ROOT/'reports';used=json.loads((REPORT/'used-assets.json').read_text('utf8'))
manifest={'assets':{},'dimensions':{},'backgroundGeometry':{},'portraitGeometry':{},'portraits':{},'backgroundNames':{}}
hashes={};audit=[];missing=[]
def save(im,key,transparent=False):
    im=im.convert('RGBA' if transparent else 'RGB')
    if transparent:
        im=im.quantize(colors=96,method=Image.Quantize.FASTOCTREE);ext='.png'
        buf=io.BytesIO();im.save(buf,format='PNG',optimize=True)
    else:
        ext='.jpg';buf=io.BytesIO();im.save(buf,format='JPEG',quality=55,optimize=True,progressive=False)
    data=buf.getvalue();digest=hashlib.sha256(data).hexdigest();name=hashes.get(digest)
    if not name:name=key+ext;hashes[digest]=name;(DEST/name).write_bytes(data)
    manifest['assets'][key]=name;manifest['dimensions'][name]=list(im.size)
    audit.append({'key':key,'file':name,'bytes':len(data),'size':list(im.size)})
bg=MPK(GAME/'bg.mpk');groups={}
for n,row in enumerate(bg.entries):
    im=Image.open(io.BytesIO(bg.read(row['id']))).convert('RGBA');alpha=im.getchannel('A').getextrema();transparent=alpha[0]<255
    key='bg'+str(row['id']);manifest['backgroundGeometry'][str(row['id'])]={'size':list(im.size),'transparent':transparent};manifest['backgroundNames'][str(row['id'])]=row['name']
    im.thumbnail((320,180),Image.Resampling.LANCZOS);save(im,key,transparent)
    name=Path(row['name']).stem
    if name.startswith('EV_'):
        m=re.match(r'(EV_[A-Z]+\d+)',name);group=m[1] if m else name;groups.setdefault(group,[]).append(key)
    if n%100==0:print('BG',n,'/',len(bg.entries),flush=True)
ch=MPK(GAME/'chara.mpk');byfile={}
for key in used['portraits']:
    file,face=map(int,key.split(':'));byfile.setdefault(file,set()).add(face)
for index,(file,faces) in enumerate(sorted(byfile.items())):
    if file==65535:continue
    source=Image.open(io.BytesIO(ch.read(file))).convert('RGBA');lay=ch.read(file+1)
    n,count=struct.unpack_from('<II',lay);assert len(lay)>=8+n*12+count*16
    states={}
    for j in range(n):
        ident,start,length=struct.unpack_from('<III',lay,8+j*12);assert start+length<=count
        states[ident]=[tuple(round(v) for v in struct.unpack_from('<4f',lay,8+n*12+(start+k)*16)) for k in range(length)]
    for face in sorted(faces):
        layers=[1,0x20000000|face,0x40000000|(face<<8),0x60000000|(face<<8),0x30000000|(face<<8)]
        chunks=[c for l in layers for c in states.get(l,[])]
        if not chunks:missing.append({'file':file,'face':face,'reason':'empty'});continue
        has_faces=any(i>>24==0x20 for i in states)
        face_layers=layers[1:]
        if has_faces and not any(l in states for l in face_layers):missing.append({'file':file,'face':face,'reason':'face absent'});continue
        x0=min(c[0] for c in chunks);y0=min(c[1] for c in chunks);x1=max(c[0]+30 for c in chunks);y1=max(c[1]+30 for c in chunks)
        assert 0<x1-x0<6000 and 0<y1-y0<6000
        canvas=Image.new('RGBA',(x1-x0,y1-y0))
        for x,y,sx,sy in chunks:
            assert 0<=sx and 0<=sy and sx+30<=source.width and sy+30<=source.height
            canvas.paste(source.crop((sx,sy,sx+30,sy+30)),(x-x0,y-y0))
        box=canvas.getbbox()
        if not box:missing.append({'file':file,'face':face,'reason':'transparent'});continue
        left,top,right,bottom=box
        # Original coordinates, including the full visible body, are retained.
        # A single proportional scale avoids the old floating-waist failure.
        im=canvas.crop(box);size=[right-left,bottom-top];im.thumbnail((200,240),Image.Resampling.LANCZOS)
        key=f'p{file}_{face}';save(im,key,True);manifest['portraits'][f'{file}:{face}']=key
        manifest['portraitGeometry'][key]={'origin':[x0+left,y0+top],'size':size,'faceLayer':not has_faces or any(l in states for l in face_layers),'source':ch.by_id[file]['name']}
    if index%40==0:print('CH',index,'/',len(byfile),flush=True)
(OUT/'assets.txt').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),'utf8')
(OUT/'gallery.txt').write_text(json.dumps([{'image':v[0],'images':v,'label':k} for k,v in groups.items()],separators=(',',':')),'utf8')
report={'sourceReadOnly':True,'backgrounds':len(bg.entries),'portraits':len(manifest['portraits']),'uniqueImages':len(hashes),'bytes':sum((DEST/f).stat().st_size for f in hashes.values()),'missing':missing,'files':audit}
(REPORT/'assets.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False),flush=True)
if missing:raise SystemExit('Unresolved portrait geometry; inspect reports/assets.json')
