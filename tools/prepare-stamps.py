from pathlib import Path
import io
from PIL import Image
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common/phone-stamps';O.mkdir(exist_ok=True)
m=MPK(R.parent/'steins0-probe/system.mpk');row=next(e for e in m.entries if e['name']=='phone_rine.dds');im=Image.open(io.BytesIO(m.read(row['id']))).convert('RGBA')
for i in range(21):
 x,y=94+(i%3)*198,4+(i//3)*172;p=im.crop((x,y,min(x+198,704),min(y+172,1212)));p.thumbnail((160,140),Image.Resampling.LANCZOS);p.quantize(colors=64,method=Image.Quantize.FASTOCTREE).save(O/f'{i}.png',optimize=True)
