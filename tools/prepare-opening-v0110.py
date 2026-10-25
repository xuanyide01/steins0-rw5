"""Modest 8 fps trial using the physically tested four-frame 6 fps layout."""
from pathlib import Path
from PIL import Image
import json,shutil,math,hashlib,io
import numpy as np
R=Path(__file__).resolve().parents[1];S=R/'src/common';B=R/'reports/before-v0110';D=R/'artwork/v0110';D.mkdir(exist_ok=True)
for rel in ['src/common/opening','src/common/opening.js','src/common/media.txt','src/pages/index/index.ux','src/manifest.json','src/config-watch.json','package.json']:
    p=B/rel
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        if (R/rel).is_dir():shutil.copytree(R/rel,p)
        else:shutil.copyfile(R/rel,p)
origin=json.loads((R/'reports/opening-v018-source.json').read_text('utf8'));fps=origin['sourceFPS'];count=math.ceil(origin['durationMilliseconds']*8/1000);rows=[];checks=[];allErrors=[]
for start in range(0,count,4):
    atlas=Image.new('RGB',(1024,144));raws=[]
    for j,i in enumerate(range(start,min(start+4,count))):
        frame=min(3310,math.floor(i*fps/8))
        with Image.open(R/'artwork/v018/raw256'/f'frame{frame:04d}.png') as im:raw=im.convert('RGB')
        atlas.paste(raw,(j*256,0));raws.append(np.asarray(raw,dtype=np.float32))
    # The first frame of each half second exists at the same time in the 6 fps build.
    oldFrame=start*3//4
    with Image.open(B/'src/common/opening'/f'{oldFrame//4:03d}.jpg') as im:old=im.convert('RGB').crop((oldFrame%4*256,0,(oldFrame%4+1)*256,144))
    previous=float(np.mean((np.asarray(old,dtype=np.float32)-raws[0])**2))
    for quality in [45,50,60,70,80,90,95,100]:
        out=io.BytesIO();atlas.save(out,'JPEG',quality=quality,optimize=True,subsampling=2);data=out.getvalue()
        with Image.open(io.BytesIO(data)) as im:decoded=im.convert('RGB')
        errors=[float(np.mean((np.asarray(decoded.crop((j*256,0,(j+1)*256,144)),dtype=np.float32)-raw)**2)) for j,raw in enumerate(raws)]
        if errors[0]<=previous+1e-6:break
    else:raise AssertionError(('Quality regression',start,previous,errors[0]))
    p=D/f'{start//4:03d}.jpg';p.write_bytes(data);rows.append({'file':p.name,'firstFrame':start,'count':len(raws),'quality':quality,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    checks.append({'frame':start,'old6FPSFrame':oldFrame,'oldMse':previous,'newMse':errors[0]});allErrors.extend(errors)
for row in rows:shutil.copyfile(D/row['file'],S/'opening'/row['file'])
report={'result':'passed','version':'0.1.10','baseVersion':'0.1.9','targetFPS':8,'targetFrames':count,'framesPerAtlas':4,'atlasCount':len(rows),'atlasSize':[1024,144],'frameSize':[256,144],'displaySize':[384,216],'displaySheetSize':[1536,216],'viewport':[24,149,384,216],'durationMilliseconds':origin['durationMilliseconds'],'imageBytes':sum(x['bytes'] for x in rows),'minimumJPEGQuality':min(x['quality'] for x in rows),'commonTemporalFramesChecked':len(checks),'allCommonFramesSourceRelativeMseNoWorse':True,'meanNewFrameMse':sum(allErrors)/len(allErrors),'singleAtlasRGBABytes':1024*144*4,'displaySheetRGBABytes':1536*216*4,'samePerImageBudgetAsTestedSixFPS':True,'audioBytesUnchanged':(S/'opening/op.mp3').read_bytes()==(B/'src/common/opening/op.mp3').read_bytes(),'atlases':rows,'commonFrameQualityChecks':checks,'physicalSixFPSFeedback':'现在可以正常播放'}
(R/'reports/opening-v0110-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['atlases','commonFrameQualityChecks']},ensure_ascii=False))
