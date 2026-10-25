"""Original SG0 title/OP/chapter assets; no standalone video is delivered."""
from pathlib import Path
import io,sys,subprocess,json,math,wave,re
from PIL import Image,ImageDraw,ImageOps
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';P=R.parent/'steins0-probe'
G=Path('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR')
FF=R.parent/'sg-media-runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
for name in ['ui','title-machine','opening','chapter-cards']:(O/name).mkdir(parents=True,exist_ok=True)
sysm=MPK(P/'system.mpk')
def system(name):return Image.open(io.BytesIO(sysm.read(next(e['id'] for e in sysm.entries if e['name']==name)))).convert('RGBA')
chip=system('title_chip.dds')
for name,top in [('start',1090),('load',1132),('extra',1173),('config',1215)]:
    chip.crop((666,top,915,top+36)).resize((180,26),Image.Resampling.LANCZOS).save(O/'ui'/f'{name}.png')
# Use the original red blueprint portraits, with the original circular zero logo.
portrait=chip.crop((96,0,900,810));portrait=ImageOps.fit(portrait,(192,192))
mask=Image.new('L',(192,192));ImageDraw.Draw(mask).ellipse((0,0,191,191),fill=255);portrait.putalpha(mask);portrait.save(O/'logo.png')
bg=Image.new('RGB',(432,514),'#111515');piece=chip.crop((1014,280,1828,1090)).resize((262,262),Image.Resampling.LANCZOS);bg.paste(piece,(170,2),piece)
bg.save(O/'title_bg.jpg',quality=83,optimize=True)
poses=[]
for k,name in enumerate(['title_logo1.dds','title_logo2.dds','title_logo3.dds']):
    im=system(name)
    for i in range(25 if k<2 else 10):poses.append(im.crop((i%5*768,i//5*768,i%5*768+768,i//5*768+768)).resize((160,160),Image.Resampling.LANCZOS))
for first in range(0,len(poses),4):
    atlas=Image.new('RGBA',(640,160))
    for j,im in enumerate(poses[first:first+4]):atlas.paste(im,(j*160,0))
    atlas.quantize(colors=96,method=Image.Quantize.FASTOCTREE).save(O/'title-machine'/f'atlas{first//4:02d}.png',optimize=True)
Image.new('RGB',(2,2),'black').save(O/'black.png');Image.new('RGB',(2,2),'white').save(O/'white.png')
def run(args):subprocess.run([str(FF),'-y','-v','error',*args],check=True)
title=R/'reports/title-original.ogg'
if not title.exists():title.write_bytes(MPK(G/'bgm.mpk').read(41))
# Derive duration from decoded PCM, then append the same protective tail as SG1.
run(['-i',str(title),'-ac','1','-ar','8000','-c:a','pcm_s16le',str(R/'reports/title-content.wav')])
with wave.open(str(R/'reports/title-content.wav')) as f:title_ms=f.getnframes()/f.getframerate()*1000
duration=title_ms/1000
run(['-i',str(title),'-af',f'afade=t=out:st={duration-.12}:d=0.12,apad=pad_dur=2','-map_metadata','-1','-ac','1','-ar','8000','-c:a','pcm_s16le',str(O/'title-piano.wav')])
# 2026-10-23: user explicitly deferred OP production. Do not convert OP or
# advertise a movie button; retain its original source cue only in the audit IR.
RAD=R.parent/'sg-media-runtime/rad/files/radvideo64.exe'
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
def rad(args):
    subprocess.run([str(RAD),'BinkConv',*map(str,args),'/O','/#'],check=True,timeout=60,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
cards=['TIT_000','TIT_001','TIT_A01','TIT_A02','TIT_A03','TIT_A04','TIT_B01','TIT_B02','TIT_B03A','TIT_B03B','TIT_B04','TIT_K01','TIT_M01','TIT_T01']
for i,name in enumerate(cards):
    raw=R/'reports'/f'card-{i}.png';rad([G/'movie/1280x720'/f'{name}.bk2',raw,'/S75','/E75','/(432','/)243','/N-1','/Z0']);Image.open(raw).convert('RGB').save(O/'chapter-cards'/f'{i}.jpg',quality=82,optimize=True)
    print('chapter card',i,flush=True)
meta={'sourceReadOnly':True,'titleSource':'_Startup_win.scs:72 BGMplay 41 = bgm221.ogg','titleContentMs':round(title_ms),'titleTailMs':2000,'titleFrames':60,'titleFPS':30,'titleTextureSources':['title_logo1.dds','title_logo2.dds','title_logo3.dds'],'openingEnabled':False,'openingDeferredByUser':True,'chapterCards':cards,'standaloneVideoExported':False}
(R/'reports/media.json').write_text(json.dumps(meta,indent=2),'utf8');(O/'media.txt').write_text(json.dumps(meta,separators=(',',':')),'utf8');print(json.dumps(meta),flush=True)
