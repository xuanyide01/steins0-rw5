from pathlib import Path
import io,json
from PIL import Image
from mpk import MPK
R=Path(__file__).resolve().parents[1];O=R/'src/common/ui';m=MPK(R.parent/'steins0-probe/system.mpk')
chip=Image.open(io.BytesIO(m.read(next(e['id'] for e in m.entries if e['name']=='title_chip.dds')))).convert('RGBA');rows=[]
for name,top in [('start',1090),('load',1132),('extra',1173),('config',1215)]:
 box=(666,top,915,top+36);p=chip.crop(box).resize((180,26),Image.Resampling.LANCZOS);p.save(O/f'{name}.png');rows.append({'name':name,'crop':box,'size':[180,26]})
(R/'reports/button-crops-v011.json').write_text(json.dumps(rows,indent=2),'utf8')
