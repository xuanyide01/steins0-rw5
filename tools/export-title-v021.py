from pathlib import Path
from PIL import Image
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';C=R/'reports/title-capture-v021'
capture=json.loads((C/'capture.json').read_text('utf8'))
frames=[Image.open(C/x['file']).convert('RGB') for x in capture['rows']]
assert len(frames)==60 and all(f.size==(432,514) for f in frames)
name='命运石之门0-REDMIWatch5-0.2.1-标题界面'
static=O/(name+'-静态.png');shutil.copyfile(C/'000.png',static)
# GIF uses one palette and the actual capture intervals; no generated/interpolated poses.
sample=Image.new('RGB',(432,514*10))
for i in range(10):sample.paste(frames[i*6],(0,i*514))
palette=sample.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
gif_frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
times=[x['atMs'] for x in capture['rows']]+[capture['elapsedMs']]
durations=[max(10,round((times[i+1]-times[i])/10)*10) for i in range(len(frames))]
gif=O/(name+'-动态.gif')
gif_frames[0].save(gif,save_all=True,append_images=gif_frames[1:],duration=durations,loop=0,optimize=True,disposal=1)
with Image.open(gif) as check:
 assert check.is_animated and check.n_frames>20 and check.size==(432,514)
 result={'kind':capture['kind'],'sourceVersion':'0.2.1','resolution':[432,514],'captureFrames':60,'gifFrames':check.n_frames,'durationMs':sum(durations),'gifPaletteColors':256,'screenRecordingNotDeviceFPSBenchmark':True,'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [static,gif]]}
(R/'reports/title-capture-v021.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
