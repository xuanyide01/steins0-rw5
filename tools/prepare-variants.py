from pathlib import Path
import json,io,hashlib
import numpy as np
from PIL import Image
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';a=json.loads((O/'assets.txt').read_text('utf8'));v=json.loads((R/'reports/raw-visuals.json').read_text('utf8'))
G=Path('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR');bg=MPK(G/'bg.mpk');masks=MPK(G/'mask.mpk')
def original(i):return Image.new('RGBA',(1920,1080),((i>>16)&255,(i>>8)&255,i&255,255)) if i<0 else Image.open(io.BytesIO(bg.read(i))).convert('RGBA')
def save(im,key):
    im.thumbnail((320,180),Image.Resampling.LANCZOS);transparent=im.getchannel('A').getextrema()[0]<255;name=key+('.png' if transparent else '.jpg')
    if transparent:im.quantize(colors=96,method=Image.Quantize.FASTOCTREE).save(O/'images'/name,optimize=True)
    else:im.convert('RGB').save(O/'images'/name,quality=55,optimize=True)
    a['assets'][key]=name;a['dimensions'][name]=list(im.size)
crops=set();ms=set();colors=set()
for view in v:
    for row in view[0]:
        if row[8]<0:colors.add(row[8])
        if row[10]==1:crops.add(tuple([row[8],row[3],row[4],row[6],row[7]]))
        if row[12] in (15,16):ms.add(tuple([row[8],row[12],row[15],row[11],row[16]]))
a['backgroundCrops']={};a['backgroundMasks']={}
for i in colors:save(Image.new('RGBA',(320,180),((i>>16)&255,(i>>8)&255,i&255,255)),'color'+str(i))
for spec in sorted(crops):
    i,x,y,w,h=spec
    if w<=0 or h<=0:continue
    k=':'.join(map(str,spec));key='c'+hashlib.sha256(k.encode()).hexdigest()[:12];save(original(i).crop(tuple(round(z*1.5) for z in (x,y,x+w,y+h))),key);a['backgroundCrops'][k]=key
for spec in sorted(ms):
    i,mode,mid,count,extent=spec;k=':'.join(map(str,spec));key='m'+hashlib.sha256(k.encode()).hexdigest()[:12];im=original(i);im.thumbnail((320,180),Image.Resampling.LANCZOS)
    m=Image.open(io.BytesIO(masks.read(mid))).convert('RGB').resize(im.size,Image.Resampling.BILINEAR);arr=np.asarray(m,dtype=np.float32)/255;light=(arr.max(axis=2)+arr.min(axis=2))/2
    if mode==16:light=1-light
    extent=extent or 16;count=max(0,min(count,extent+256));factor=np.clip(light*(256/extent)-(1-count/255)*(256/extent),0,1);old=np.asarray(im.getchannel('A'),dtype=np.float32);im.putalpha(Image.fromarray(np.round(old*factor).astype('uint8')));save(im,key);a['backgroundMasks'][k]=key
(O/'assets.txt').write_text(json.dumps(a,ensure_ascii=False,separators=(',',':')),'utf8');print('variants',len(crops),len(ms),len(colors))
