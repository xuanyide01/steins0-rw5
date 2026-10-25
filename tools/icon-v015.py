"""Crop the requested original illustration into the circular launcher asset."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'reports/icon-v015';source=D/'amadeus-wallpaper-1920.jpg';im=Image.open(source).convert('RGB');box=(1110,0,1830,720)
assert im.size==(1920,1080)
crop=im.crop(box);mask=Image.new('L',(768,768));ImageDraw.Draw(mask).ellipse((0,0,767,767),fill=255)
icon=crop.resize((192,192),Image.Resampling.LANCZOS).convert('RGBA');icon.putalpha(mask.resize((192,192),Image.Resampling.LANCZOS));icon.save(R/'src/common/logo.png',optimize=True)
preview=crop.resize((384,384),Image.Resampling.LANCZOS).convert('RGBA');preview.putalpha(mask.resize((384,384),Image.Resampling.LANCZOS));preview.save(D/'icon-preview.png')
report={'sourcePage':'https://www.goodfon.ru/other-anime/wallpaper-download-1920x1080-kurisu-makise-makise-kurisu.html','imageURL':'https://img.goodfon.ru/original/1920x1080/f/cd/kurisu-makise-makise-kurisu.jpg','officialCoverReference':'https://music.ani-tone.com/release/FVCG-1354/','identification':'Amadeus / Kanako Ito / FVCG-1354; illustration by huke','originalSourcePixels':[1920,1080],'crop':list(box),'launcherSize':[192,192],'textOutsideCrop':True,'originalWallpaperContainsText':True,'circleAlpha':True,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()}
(R/'reports/icon-v015.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
