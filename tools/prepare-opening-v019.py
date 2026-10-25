"""Halve temporal work and atlas height; prove retained pictures are no worse."""
from pathlib import Path
from PIL import Image
import json,shutil,hashlib,io,math
import numpy as np
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v019';S=R/'src/common';A=R/'artwork/v018';D=R/'artwork/v019';D.mkdir(exist_ok=True)
for rel in ['src/common/opening','src/common/opening.js','src/common/media.txt','src/pages/index/index.ux','src/manifest.json','src/config-watch.json','package.json']:
    src=R/rel;out=B/rel
    if not out.exists():
        out.parent.mkdir(parents=True,exist_ok=True)
        if src.is_dir():shutil.copytree(src,out)
        else:shutil.copyfile(src,out)
old=json.loads((R/'reports/opening-v018-source.json').read_text('utf8'));fps=old['sourceFPS'];count=math.ceil(old['durationMilliseconds']*6/1000);rows=[];errors=[]
for start in range(0,count,4):
    atlas=Image.new('RGB',(1024,144));originals=[];oldErrors=[]
    with Image.open(B/'src/common/opening'/f'{start//4:03d}.jpg') as im:baseline=im.convert('RGB')
    for j,i in enumerate(range(start,min(start+4,count))):
        index=min(3310,math.floor(i*fps/6))
        with Image.open(A/'raw256'/f'frame{index:04d}.png') as im:raw=im.convert('RGB')
        atlas.paste(raw,(j*256,0));a=np.asarray(raw,dtype=np.float32);originals.append(a)
        tile=j*2;oldImage=baseline.crop(((tile%4)*256,(tile//4)*144,(tile%4+1)*256,(tile//4+1)*144))
        oldErrors.append(float(np.mean((np.asarray(oldImage,dtype=np.float32)-a)**2)))
    selected=None
    for quality in [45,50,60,70,80,90,95,100]:
        buf=io.BytesIO();atlas.save(buf,'JPEG',quality=quality,optimize=True,subsampling=2);data=buf.getvalue()
        with Image.open(io.BytesIO(data)) as im:decoded=im.convert('RGB')
        newErrors=[float(np.mean((np.asarray(decoded.crop((j*256,0,(j+1)*256,144)),dtype=np.float32)-raw)**2)) for j,raw in enumerate(originals)]
        if all(new<=previous+1e-6 for new,previous in zip(newErrors,oldErrors)):selected=(quality,data,newErrors);break
    assert selected is not None,('Cannot preserve quality',start,oldErrors,newErrors)
    quality,data,newErrors=selected;p=D/f'{start//4:03d}.jpg';p.write_bytes(data)
    rows.append({'file':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'quality':quality,'firstFrame':start,'count':len(originals)})
    errors.extend({'frame':start+j,'oldFrame':2*(start+j),'oldMse':a,'newMse':b} for j,(a,b) in enumerate(zip(oldErrors,newErrors)))
for row in rows:shutil.copyfile(D/row['file'],S/'opening'/row['file'])
report={'result':'passed','baseVersion':'0.1.8','sourceReadOnly':True,'targetFPS':6,'targetFrames':count,'framesPerAtlas':4,'atlasCount':len(rows),'frameSize':[256,144],'atlasSize':[1024,144],'displaySheetSize':[1536,216],'displaySize':[384,216],'viewport':[24,149,384,216],'durationMilliseconds':old['durationMilliseconds'],'imageBytes':sum(x['bytes'] for x in rows),'allRetainedFramesSourceRelativeMseNoWorse':True,'retainedFrameChecks':len(errors),'meanOldMse':sum(x['oldMse'] for x in errors)/len(errors),'meanNewMse':sum(x['newMse'] for x in errors)/len(errors),'singleAtlasRGBABytes':1024*144*4,'displaySheetRGBABytes':1536*216*4,'fileCountUnchanged':len(rows)==old['atlasCount'],'audioBytesUnchanged':(S/'opening/op.mp3').read_bytes()==(B/'src/common/opening/op.mp3').read_bytes(),'atlases':rows,'qualityChecks':errors}
(R/'reports/opening-v019-source.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['atlases','qualityChecks']},ensure_ascii=False))
