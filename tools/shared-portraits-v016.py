"""Probe shared body/expression textures against original SG0 pixels, never altering originals."""
from pathlib import Path
import io,json,re,struct,sys,hashlib,collections,shutil
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';D=R/'reports/shared-portraits-v016';D.mkdir(exist_ok=True);B=R/'reports/before-v016';baseline=B/'portrait-assets.js'
if not baseline.exists():shutil.copyfile(O/'assets.js',baseline)
mapping=json.loads(re.search(r'const assets=(.*);',baseline.read_text('utf8')).group(1));a=json.loads((O/'assets.txt').read_text('utf8'));ch=MPK('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR/chara.mpk')
sample='--sample' in sys.argv;apply='--apply' in sys.argv;groups=collections.defaultdict(list)
for key,geo in a['portraitGeometry'].items():
    if key in mapping:groups[int(key[1:].split('_')[0])].append(key)
def encode(im):
    arr=np.asarray(im);colors,inv=np.unique(arr.reshape(-1,4),axis=0,return_inverse=True)
    if len(colors)<=256:
        result=Image.fromarray(inv.reshape(im.height,im.width).astype('uint8'),'P');result.putpalette(colors[:,:3].flatten().tolist());result.info['transparency']=colors[:,3].tobytes()
    else:result=im
    b=io.BytesIO();result.save(b,format='PNG',optimize=True);data=b.getvalue();assert Image.open(io.BytesIO(data)).convert('RGBA').tobytes()==im.tobytes();return data
def mse(x,y):
    left=np.asarray(x,dtype='float32');right=np.asarray(y,dtype='float32');left=left[:,:,:3]*left[:,:,3:]/255+48*(1-left[:,:,3:]/255);right=right[:,:,:3]*right[:,:,3:]/255+48*(1-right[:,:,3:]/255)
    return float(np.mean((left-right)**2))
def image(file):
    p=O/'img'/file;return Image.open(p if p.exists() else B/'portrait-originals'/file).convert('RGBA')
rows=[];parts={};files={};beforeTotal=0;afterTotal=0
def store(data):
    h=hashlib.sha256(data).hexdigest();rel='shared/'+str(len(files)//40)+'/'+str(len(files)%40)+'.png'
    if h in files:return files[h]['file']
    files[h]={'file':rel,'data':data};return rel
for index,(file,keys) in enumerate(sorted(groups.items())):
    if len(keys)<2 or sample and file not in [0,6,114,120,138,158,578]:continue
    source=Image.open(io.BytesIO(ch.read(file))).convert('RGBA');lay=ch.read(file+1);n,count=struct.unpack_from('<II',lay);states={}
    for j in range(n):
        ident,start,length=struct.unpack_from('<III',lay,8+j*12);states[ident]=[tuple(round(v) for v in struct.unpack_from('<4f',lay,8+n*12+(start+k)*16)) for k in range(length)]
    geometry=collections.defaultdict(list)
    for key in keys:
        geo=a['portraitGeometry'][key];geometry[tuple(geo['origin']+geo['size'])].append(key)
    for same in geometry.values():
        if len(same)<2:continue
        same=sorted(same,key=lambda k:int(k.split('_')[1]));originals=[];old=[]
        for key in same:
            face=int(key.split('_')[1]);chunks=[c for l in [1,0x20000000|face,0x40000000|(face<<8),0x60000000|(face<<8),0x30000000|(face<<8)] for c in states.get(l,[])];x0=min(c[0] for c in chunks);y0=min(c[1] for c in chunks);x1=max(c[0]+30 for c in chunks);y1=max(c[1]+30 for c in chunks);canvas=Image.new('RGBA',(x1-x0,y1-y0))
            for x,y,sx,sy in chunks:canvas.paste(source.crop((sx,sy,sx+30,sy+30)),(x-x0,y-y0))
            im=canvas.crop(canvas.getbbox());im.thumbnail((200,240),Image.Resampling.LANCZOS);originals.append(im);old.append(image(mapping[key]));assert im.size==old[-1].size
        pixels=np.concatenate([np.asarray(im)[:,:,:3][np.asarray(im)[:,:,3]>128] for im in originals]);palette=Image.fromarray(pixels.reshape(1,-1,3)).quantize(colors=128,method=Image.Quantize.MEDIANCUT);pal=np.array(palette.getpalette(),dtype='uint8').reshape(-1,3);converted=[]
        for im in originals:
            raw=np.asarray(im);rgb=pal[np.asarray(im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE))];alpha=np.where(raw[:,:,3]<32,0,np.where(raw[:,:,3]<192,128,255)).astype('uint8');rgba=np.concatenate([rgb,alpha[:,:,None]],axis=2);rgba[alpha==0]=0;converted.append(Image.fromarray(rgba,'RGBA'))
        base=converted[0];baseArr=np.asarray(base);baseData=encode(base);local=[];newSize=len(baseData);oldSize=0
        if mse(originals[0],base)>mse(originals[0],old[0]):continue
        for i,key in enumerate(same):
            oldBytes=(O/'img'/mapping[key]).stat().st_size if (O/'img'/mapping[key]).exists() else (B/'portrait-originals'/mapping[key]).stat().st_size;oldSize+=oldBytes;target=converted[i];arr=np.asarray(target);changed=np.any(arr!=baseArr,axis=2)
            if np.any(changed&(arr[:,:,3]!=255)) or mse(originals[i],target)>mse(originals[i],old[i]):local.append((key,None,None));newSize+=oldBytes;continue
            patchData=None
            if changed.any():
                mask=np.asarray(Image.fromarray((changed*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0;mask&=arr[:,:,3]==255;patch=np.zeros_like(arr);patch[mask]=arr[mask];overlay=Image.fromarray(patch,'RGBA');combined=Image.alpha_composite(base,overlay);assert combined.tobytes()==target.tobytes();patchData=encode(overlay);newSize+=len(patchData)
            local.append((key,baseData,patchData))
        if newSize>=oldSize:continue
        baseRel=store(baseData)
        for i,(key,data,patchData) in enumerate(local):
            if data is None:continue
            sequence=[baseRel]+([store(patchData)] if patchData else []);parts[key]=sequence;rows.append({'key':key,'original':mapping[key],'parts':sequence,'size':list(originals[i].size),'targetRGBASha256':hashlib.sha256(converted[i].tobytes()).hexdigest(),'oldMse':mse(originals[i],old[i]),'newMse':mse(originals[i],converted[i]),'source':a['portraitGeometry'][key]['source']})
        beforeTotal+=oldSize;afterTotal+=newSize
        if sample:
            board=Image.new('RGB',(originals[0].width*3,originals[0].height+22),'#303030');draw=ImageDraw.Draw(board)
            for col,(label,im) in enumerate([('source resized',originals[0]),('v0.1.5',old[0]),('shared128',base)]):board.paste(im,(col*im.width,22),im);draw.text((col*im.width,3),label,fill='white')
            board.save(D/(same[0]+'-compare.png'))
    if index%40==0:print('actors',index,'/',len(groups),flush=True)
if 'p120_1' in parts:assert len(parts['p120_1'])==1
for item in files.values():
    p=D/item['file'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(item['data'])
report={'sampleOnly':sample,'apply':apply,'convertedFaces':len(rows),'uniqueTextures':len(files),'beforeBytesInSelectedGroups':beforeTotal,'afterBytesInSelectedGroups':afterTotal,'saving':beforeTotal-afterTotal,'allSourceRelativeMseNoWorse':True,'dimensionsAndCoordinatesUnchanged':True,'rows':rows,'parts':parts}
(D/('sample.json' if sample else 'full.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','parts']},ensure_ascii=False))
if apply:
    for item in files.values():p=O/'img'/item['file'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(item['data'])
    for key,sequence in parts.items():mapping[key]=sequence[0]
    used=set(mapping.values())|{f for sequence in parts.values() for f in sequence}
    for row in rows:
        oldFile=row['original']
        if oldFile in used:continue
        p=(O/'img'/oldFile).resolve();assert p.is_relative_to((O/'img').resolve());backup=B/'portrait-originals'/oldFile;backup.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():shutil.move(str(p),str(backup))
    (O/'assets.js').write_text('const assets='+json.dumps(mapping,separators=(',',':'))+';\nconst parts='+json.dumps(parts,separators=(',',':'))+";\nexport function imagePath(key){return assets[key]?'/common/img/'+assets[key]:'/common/black.png';}\nexport function imagePaths(key){return parts[key]?parts[key].map(f=>'/common/img/'+f):[imagePath(key)];}\n",encoding='utf8')
