"""Reconstruct SG0 portraits directly; retain decoded dimensions and bounded palette PNGs."""
from pathlib import Path
import io,json,re,struct,sys,zipfile
import numpy as np
from PIL import Image,ImageDraw
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';D=R/'reports/portraits-v013';D.mkdir(exist_ok=True)
a=json.loads((O/'assets.txt').read_text('utf8'));mapping=json.loads(re.search(r'const assets=(.*);',(O/'assets.js').read_text('utf8')).group(1))
ch=MPK('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR/chara.mpk')
old=zipfile.ZipFile(R.parents[1]/'outputs/命运石之门0-REDMIWatch5-0.1.2-源码与检查.zip')
def quant(im,colors):
    arr=np.asarray(im);visible=arr[:,:,3]>128
    # Train on visible original pixels only; transparent black must not consume skin/clothing colours.
    pixels=arr[:,:,:3][visible];palette=Image.fromarray(pixels.reshape(1,-1,3)).quantize(colors=colors,method=Image.Quantize.MEDIANCUT)
    rgb=im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE)
    indices=np.asarray(rgb);alpha=np.where(arr[:,:,3]<32,0,np.where(arr[:,:,3]<192,128,255)).astype('uint8')
    pairs=np.stack([indices.flatten(),alpha.flatten()],axis=1);pairs[alpha.flatten()==0]=0
    unique,inv=np.unique(pairs,axis=0,return_inverse=True);assert len(unique)<=256
    pal=np.array(palette.getpalette(),dtype='uint8').reshape(-1,3)
    out=Image.fromarray(inv.reshape(im.height,im.width).astype('uint8'),'P');out.putpalette(pal[unique[:,0]].flatten().tolist())
    out.info['transparency']=unique[:,1].tobytes();buf=io.BytesIO();out.save(buf,format='PNG',optimize=True);return buf.getvalue()
def mse(im,data):
    x=np.asarray(im,dtype='float32');y=np.asarray(Image.open(io.BytesIO(data)).convert('RGBA'),dtype='float32')
    # Composite both on mid-gray, includes transparency-edge errors.
    x=x[:,:,:3]*x[:,:,3:]/255+48*(1-x[:,:,3:]/255);y=y[:,:,:3]*y[:,:,3:]/255+48*(1-y[:,:,3:]/255)
    return float(np.mean((x-y)**2))
sample='--sample' in sys.argv;rows=[];last=None
keys=['p158_1','p120_1','p138_1'] if sample else list(a['portraitGeometry'])
for index,key in enumerate(keys):
    file,face=map(int,key[1:].split('_'))
    if file!=last:
        source=Image.open(io.BytesIO(ch.read(file))).convert('RGBA');lay=ch.read(file+1);n,count=struct.unpack_from('<II',lay);states={}
        for j in range(n):
            ident,start,length=struct.unpack_from('<III',lay,8+j*12)
            states[ident]=[tuple(round(v) for v in struct.unpack_from('<4f',lay,8+n*12+(start+k)*16)) for k in range(length)]
        last=file
    chunks=[c for l in [1,0x20000000|face,0x40000000|(face<<8),0x60000000|(face<<8),0x30000000|(face<<8)] for c in states.get(l,[])]
    x0=min(c[0] for c in chunks);y0=min(c[1] for c in chunks);x1=max(c[0]+30 for c in chunks);y1=max(c[1]+30 for c in chunks)
    canvas=Image.new('RGBA',(x1-x0,y1-y0))
    for x,y,sx,sy in chunks:canvas.paste(source.crop((sx,sy,sx+30,sy+30)),(x-x0,y-y0))
    im=canvas.crop(canvas.getbbox());im.thumbnail((200,240),Image.Resampling.LANCZOS)
    path='src/common/img/'+mapping[key];before=old.read(path);assert Image.open(io.BytesIO(before)).size==im.size
    candidates=[(c,quant(im,c)) for c in ([40,48,56,64,80,96] if sample else [32,40,48,64])]
    metrics=[{'colors':c,'bytes':len(data),'mse':mse(im,data)} for c,data in candidates]
    for c,data in candidates:
        p=D/str(c)/mapping[key];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    rows.append({'key':key,'path':mapping[key],'beforeBytes':len(before),'beforeMse':mse(im,before),'size':list(im.size),'candidates':metrics})
    if sample:
        board=Image.new('RGB',(im.width*4,im.height+25),'#303030');draw=ImageDraw.Draw(board)
        for i,(label,data) in enumerate([('original resized',None),('0.1.2 / 64',before),('median 48',candidates[1][1]),('median 64',candidates[3][1])]):
            pic=im if data is None else Image.open(io.BytesIO(data)).convert('RGBA');board.paste(pic,(i*im.width,25),pic);draw.text((i*im.width+3,4),label,fill='white')
        board.save(D/(key+'-comparison.png'))
    if index%100==0:print('portraits',index,'/',len(keys),flush=True)
(D/('samples.json' if sample else 'candidates.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
print('DONE',len(rows),flush=True)
