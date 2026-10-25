from pathlib import Path
import json,re,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'src/common';report=json.loads((R/'reports/shared-portraits-v016.json').read_text('utf8'));source=(O/'assets.js').read_text('utf8');mapping=json.loads(re.search(r'const assets=(.*);',source).group(1));parts=json.loads(re.search(r'const parts=(.*);',source).group(1));images={}
def image(rel):
    if rel not in images:images[rel]=Image.open(O/'img'/rel).convert('RGBA')
    return images[rel]
for row in report['rows']:
    assert parts[row['key']]==row['parts'];target=image(row['parts'][0])
    if len(row['parts'])>1:target=Image.alpha_composite(target,image(row['parts'][1]))
    assert list(target.size)==row['size'];assert hashlib.sha256(target.tobytes()).hexdigest()==row['targetRGBASha256'];assert row['newMse']<=row['oldMse']
g=json.loads((O/'graph.txt').read_text('utf8'));maxPlanes=0;maxDecoded=0;fading=0
for n in g['nodes'].values():
    for chunk in n['chunks']:
        for view in json.loads((O/'story'/chunk['file']).read_text('utf8'))['views']:
            files=[]
            for layer in view:
                key=layer[0];paths=parts.get(key,[mapping[key]])
                if layer[5]!=1000 and key.startswith('p'):assert len(paths)==1;fading+=1
                files+=paths
            maxPlanes=max(maxPlanes,len(files));maxDecoded=max(maxDecoded,sum(image(f).width*image(f).height*4 for f in set(files)))
assert len(parts.get('p120_1',[mapping['p120_1']]))==1
result={'result':'passed','compositeRGBASha256Checks':len(report['rows']),'allSharedPosesSourceRelativeMseNoWorse':True,'partialOpacityUsesOriginalSingleTexture':fading,'maximumSceneImagePlanes':maxPlanes,'maximumUniqueTextureRGBABytes':maxDecoded,'decodedBudgetIsConservativeNotMeasuredHeap':True,'amadeusCanonicalFacePreserved':True}
(R/'reports/shared-tests-v016.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
