from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'native-test-results-v0110';native=json.loads((D/'report.json').read_text('utf8'))
assert native['result'] in ['passed-awaiting-visual-review','passed']
assert native['sha256']==hashlib.sha256((R/'dist/com.codex.steins0.rw5.debug.0.1.10.rpk').read_bytes()).hexdigest()
checks=[]
for name in ['02-story-op-10s.png','02-story-op-40s.png','02-story-op-80s.png','07-muted-extra-op.png']:
    a=np.asarray(Image.open(D/name).convert('RGB'));assert a.shape==(514,432,3)
    mask=np.ones((514,432),dtype=bool);mask[149:365,24:408]=False
    maximum=int(a[mask].max());assert maximum<=3,(name,maximum)
    checks.append({'file':name,'outsideViewportMaxRGB':maximum,'sha256':hashlib.sha256((D/name).read_bytes()).hexdigest()})
assert len(set(x['sha256'] for x in checks[:3]))==3
report={'result':'passed','blackSurroundAndNoDialogueOrControlsOnOP':True,'centeredViewport':[24,149,384,216],'distinctMovingFramesCaptured':3,'screenshots':checks,'physicalDeviceTested':False}
(R/'reports/opening-pixels-v0110.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
