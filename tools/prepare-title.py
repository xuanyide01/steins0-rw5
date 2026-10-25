from pathlib import Path
import io,json
from PIL import Image
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common';m=MPK(R.parent/'steins0-probe/system.mpk')
def get(name):return Image.open(io.BytesIO(m.read(next(e['id'] for e in m.entries if e['name']==name)))).convert('RGBA')
chip=get('title_chip.dds');bg=Image.new('RGBA',(1152,688),'black');left=chip.crop((96,0,900,810)).resize((652,657),Image.Resampling.LANCZOS);right=chip.crop((1014,280,1828,1090)).resize((652,649),Image.Resampling.LANCZOS);bg.alpha_composite(left,(-120,-5));bg.alpha_composite(right,(648,122));scaled=bg.resize((432,258),Image.Resampling.LANCZOS);page=Image.new('RGB',(432,514),'black');page.paste(scaled,(0,0));page.save(O/'title_bg.jpg',quality=87,optimize=True)
sheet=get('title_logo3.dds');part=sheet.crop((0,1536,3840,2304));logo=part.crop(part.getchannel('A').getbbox()).resize((400,108),Image.Resampling.LANCZOS);logo.save(O/'title-wordmark.png',optimize=True)
poses=[]
for k,name in enumerate(['title_logo1.dds','title_logo2.dds','title_logo3.dds']):
 im=get(name)
 for i in range(25 if k<2 else 10):poses.append(im.crop((i%5*768,i//5*768,i%5*768+768,i//5*768+768)).resize((192,192),Image.Resampling.LANCZOS))
for first in range(0,60,4):
 atlas=Image.new('RGBA',(768,192))
 for j,im in enumerate(poses[first:first+4]):atlas.paste(im,(j*192,0))
 atlas.quantize(colors=64,method=Image.Quantize.FASTOCTREE).save(O/'title-machine'/f'atlas{first//4:02d}.png',optimize=True)
preview=page.convert('RGBA');preview.alpha_composite(poses[15].resize((256,256),Image.Resampling.LANCZOS),(74,0));preview.alpha_composite(logo,(16,87));preview.convert('RGB').save(R/'reports/full-title-composite.jpg',quality=93)
meta=json.loads((O/'media.txt').read_text('utf8'));meta.update(titleComposition='Original red character panels, original static wordmark above all 60 rotating zero frames',titleFrameSize=192,titleDisplaySize=256);(O/'media.txt').write_text(json.dumps(meta,separators=(',',':')),'utf8');(R/'reports/media.json').write_text(json.dumps(meta,indent=2),'utf8')
print('FULL_TITLE',sum(p.stat().st_size for p in (O/'title-machine').glob('*.png')))
