"""Read original SG0 archives only; write bounded diagnostic assets to this project."""
from pathlib import Path
import io,json,hashlib
from PIL import Image,ImageDraw,ImageFont
from mpk import MPK
R=Path(__file__).resolve().parents[1];G=Path('G:/SteamLibrary/steamapps/common/STEINS;GATE 0/USRDIR');O=R/'reports/original-v012';O.mkdir(exist_ok=True)
a=json.loads((R/'src/common/assets.txt').read_text('utf8'));ch=MPK(G/'chara.mpk');system=MPK(G/'system.mpk');bg=MPK(G/'bg.mpk')
inventory={'source':'STEINS;GATE 0/USRDIR','chara':ch.entries,'system':system.entries,'bg':bg.entries}
(O/'inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
seen={}
for key,geo in a['portraitGeometry'].items():
    if geo['source'].startswith(('DAR_','CRS_')) and geo['source'] not in seen:seen[geo['source']]=key
im=Image.new('RGB',(1000,((len(seen)+7)//8)*210),'#333333');d=ImageDraw.Draw(im)
for i,(name,key) in enumerate(sorted(seen.items())):
    pic=Image.open(R/'reports/master-images'/a['assets'][key]).convert('RGBA');pic.thumbnail((120,177));x=(i%8)*125;y=(i//8)*210;im.paste(pic,(x+(125-pic.width)//2,y),pic);d.text((x+2,y+180),name,fill='white')
im.save(O/'daru-kurisu-portraits.jpg',quality=90)
for ident in [592,676]:
    pic=Image.open(io.BytesIO(bg.read(ident))).convert('RGBA');pic.thumbnail((480,270));pic.save(O/f'bg-{ident}.png')
print(json.dumps({'portraitSheetCount':len(seen),'phoneSheets':[x for x in system.entries if any(y in x['name'].lower() for y in ['phone','amadeus'])]},ensure_ascii=False))
