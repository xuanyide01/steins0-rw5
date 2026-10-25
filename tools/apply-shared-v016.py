from pathlib import Path
import json,re,shutil
R=Path(__file__).resolve().parents[1];O=R/'src/common';B=R/'reports/before-v016';D=R/'reports/shared-portraits-v016';report=json.loads((D/'full.json').read_text('utf8'));mapping=json.loads(re.search(r'const assets=(.*);',(B/'portrait-assets.js').read_text('utf8')).group(1));parts=report['parts']
assert not report['sampleOnly'] and report['allSourceRelativeMseNoWorse']
# Separate images with per-image opacity do not equal group opacity. Keep the
# original full texture for all fading poses; only fully opaque poses are split.
fading=set()
for node in json.loads((O/'graph.txt').read_text('utf8'))['nodes'].values():
    for chunk in node['chunks']:
        for view in json.loads((O/'story'/chunk['file']).read_text('utf8'))['views']:
            for layer in view:
                if layer[0].startswith('p') and layer[5]!=1000:fading.add(layer[0])
for key in fading:
    parts.pop(key,None);old=mapping[key];p=O/'img'/old
    if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/'portrait-originals'/old,p)
report['rows']=[row for row in report['rows'] if row['key'] not in fading];report['convertedFaces']=len(report['rows']);report['retainedOriginalFadingKeys']=sorted(fading)
for rel in {p for seq in parts.values() for p in seq}:
    target=O/'img'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(D/rel,target)
for key,sequence in parts.items():mapping[key]=sequence[0]
used=set(mapping.values())|{p for seq in parts.values() for p in seq}
removed=set()
for row in report['rows']:
    old=row['original']
    if old in used or old in removed:continue
    p=(O/'img'/old).resolve();assert p.is_relative_to((O/'img').resolve());backup=B/'portrait-originals'/old;backup.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():shutil.move(str(p),str(backup))
    removed.add(old)
(O/'assets.js').write_text('const assets='+json.dumps(mapping,separators=(',',':'))+';\nconst parts='+json.dumps(parts,separators=(',',':'))+";\nexport function imagePath(key){return assets[key]?'/common/img/'+assets[key]:'/common/black.png';}\nexport function imagePaths(key){return parts[key]?parts[key].map(f=>'/common/img/'+f):[imagePath(key)];}\n",encoding='utf8')
report['applied']=True;report['removedOriginalFiles']=len(removed);report['meanOldMse']=sum(r['oldMse'] for r in report['rows'])/len(report['rows']);report['meanNewMse']=sum(r['newMse'] for r in report['rows'])/len(report['rows']);(R/'reports/shared-portraits-v016.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','parts']},ensure_ascii=False))
