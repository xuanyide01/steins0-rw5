"""Build bounded 12 fps OP atlases from read-only original Bink-decoded frames."""
from pathlib import Path
from PIL import Image
import json,math,hashlib,struct,shutil
R=Path(__file__).resolve().parents[1];A=R/'artwork/v018';O=R/'src/common/opening';O.mkdir(exist_ok=True)
source=A/'OP.bk2';header=struct.unpack('<4s15I',source.read_bytes()[:64]);count=header[2];fps=header[7]/header[8];duration=count/fps*1000
raw=sorted((A/'raw256').glob('frame*.png'));assert len(raw)==count==3311
frames=math.ceil(duration*12/1000);candidates=[]
for width,height,quality in [(256,144,30),(256,144,35)]:
    dest=A/f'atlas-{width}-q{quality}';dest.mkdir(exist_ok=True);rows=[]
    for start in range(0,frames,8):
        atlas=Image.new('RGB',(width*4,height*2))
        for j,frame in enumerate(range(start,min(start+8,frames))):
            original=min(count-1,math.floor(frame*fps/12))
            with Image.open(raw[original]) as im:
                target=im.convert('RGB')
                if target.size!=(width,height):target=target.resize((width,height),Image.Resampling.LANCZOS)
                atlas.paste(target,(j%4*width,j//4*height))
        out=dest/f'{start//8:03d}.jpg';atlas.save(out,quality=quality,optimize=True,subsampling=2)
        rows.append({'file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'firstFrame':start,'count':min(8,frames-start)})
    total=sum(r['bytes'] for r in rows);candidates.append({'directory':str(dest.relative_to(R)),'frameSize':[width,height],'quality':quality,'imageBytes':total,'rows':rows})
    print(width,quality,total,flush=True)
selected=next((c for c in reversed(candidates) if c['imageBytes']<7_000_000),min(candidates,key=lambda c:c['imageBytes']))
for row in selected['rows']:shutil.copyfile(R/selected['directory']/row['file'],O/row['file'])
shutil.copyfile(A/'op.mp3',O/'op.mp3')
report={'result':'prepared','source':'Steam USRDIR/movie/1280x720/OP.bk2','sourceBytes':source.stat().st_size,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceFrames':count,'sourceFPS':fps,'durationMilliseconds':duration,'targetFPS':12,'targetFrames':frames,'framesPerAtlas':8,'atlasCount':len(selected['rows']),'frameSize':selected['frameSize'],'displaySize':[384,216],'viewport':[24,149,384,216],'quality':selected['quality'],'imageBytes':selected['imageBytes'],'audioBytes':(O/'op.mp3').stat().st_size,'audioSHA256':hashlib.sha256((O/'op.mp3').read_bytes()).hexdigest(),'audioCodec':'MP3 22050 Hz mono 48 kbps','rawGraphOpeningCue':{'node':'n0','cursor':934},'sourceReadOnly':True,'standaloneVideoExported':False,'candidates':[{k:v for k,v in c.items() if k!='rows'} for c in candidates],'atlases':selected['rows']}
(R/'reports/opening-v018-source.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['atlases','candidates']},ensure_ascii=False))
