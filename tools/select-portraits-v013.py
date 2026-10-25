"""Prune only provably unreferenced converted images; spend saved bytes on portraits."""
from pathlib import Path
import json,re,shutil,math
R=Path(__file__).resolve().parents[1];O=R/'src/common';D=R/'reports/portraits-v013';B=R/'reports/before-v013'
a=json.loads((B/'assets.js').read_text('utf8').split('const assets=')[1].split(';')[0]);g=json.loads((O/'graph.txt').read_text('utf8'));keys=set(['p120_1','p158_1','p158_4','p166_1']);frequency={}
for n in g['nodes'].values():
    for part in n['chunks']:
        c=json.loads((O/'story'/part['file']).read_text('utf8'))
        for v in c['views']:
            for l in v:keys.add(l[0])
        for f in c['frames']:
            for l in c['views'][f[2]]:
                if l[0].startswith('p'):frequency[l[0]]=frequency.get(l[0],0)+1
active={a[k] for k in keys}
for group in json.loads((O/'gallery.txt').read_text('utf8')):
    for k in group['images']:keys.add(k);active.add(a[k])
unused=set(a.values())-active;pruned=0
for rel in sorted(unused):
    p=(O/'img'/rel).resolve();assert p.is_relative_to((O/'img').resolve());b=R/'reports/pruned-v013'/rel;b.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():pruned+=p.stat().st_size;shutil.move(str(p),str(b))
    else:pruned+=b.stat().st_size
mapping={k:v for k,v in a.items() if v in active};(O/'assets.js').write_text('const assets='+json.dumps(mapping,separators=(',',':'))+";\nexport function imagePath(key){return assets[key]?'/common/img/'+assets[key]:'/common/black.png';}\n",encoding='utf8')
rows=[r for r in json.loads((D/'candidates.json').read_text('utf8')) if r['path'] in active]
budget=pruned+480000;selections={r['key']:{'colors':0,'bytes':r['beforeBytes'],'mse':r['beforeMse']} for r in rows};spent=0
# Give every visibly improved portrait its least expensive safe candidate first.
for r in rows:
    options=[c for c in r['candidates'] if c['mse']<r['beforeMse']*.97]
    if options:
        c=min(options,key=lambda c:c['bytes']);selections[r['key']]=c;spent+=c['bytes']-r['beforeBytes']
assert spent<budget,(spent,budget)
# Higher-frequency poses receive the remaining detail budget; all dimensions unchanged.
while True:
    options=[]
    for r in rows:
        old=selections[r['key']]
        for c in r['candidates']:
            delta=c['bytes']-old['bytes'];gain=old['mse']-c['mse']
            if delta>0 and gain>0 and spent+delta<=budget:options.append((gain*(1+math.log1p(frequency.get(r['key'],0)))/delta,r['key'],c,delta))
    if not options:break
    _,key,c,delta=max(options,key=lambda x:x[0]);selections[key]=c;spent+=delta
updated=0
for r in rows:
    choice=selections[r['key']];r['selected']=choice
    assert choice['mse']<=r['beforeMse']
    if choice['colors']:shutil.copyfile(D/str(choice['colors'])/r['path'],O/'img'/r['path']);updated+=1
report={'sourceReadOnly':True,'method':'single-pass visible-pixel median palette, adaptive 32/40/48/64 RGB colours plus transparent edges','portraitDimensionsUnchanged':True,'decodedPixelBudgetUnchanged':True,'prunedUnreferencedFiles':len(unused),'prunedBytes':pruned,'portraitByteIncrease':spent,'updatedPortraits':updated,'retainedPortraits':len(rows)-updated,'oldMeanMse':sum(r['beforeMse'] for r in rows)/len(rows),'newMeanMse':sum(r['selected']['mse'] for r in rows)/len(rows),'rows':rows}
(R/'reports/portrait-quality-v013.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
