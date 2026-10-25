from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v019';p=R/'src/pages/index/index.ux';s=(B/'src/pages/index/index.ux').read_text('utf8')
s=s.replace('top:{{openingTop}}px;','top:0px;',1)
s=s.replace('(src,left,top)=>{this.openingSrc=src;this.openingLeft=left;this.openingTop=top;}', '(src,left)=>{if(this.openingSrc!==src)this.openingSrc=src;if(this.openingLeft!==left)this.openingLeft=left;}')
s=s.replace('.opening-sheet{position:absolute;top:0px;width:1536px;height:432px;', '.opening-sheet{position:absolute;top:0px;width:1536px;height:216px;')
p.write_text(s,encoding='utf8')
for rel in ['src/manifest.json','src/config-watch.json','package.json']:
 p=R/rel;v=json.loads(p.read_text('utf8'))
 if 'version' in v:v['version']='0.1.9';v['scripts']['test']=v['scripts']['test'].replace('test-ui-v018.cjs','test-ui-v019.cjs')
 else:v.update(versionName='0.1.9',versionCode=13)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=R/'src/common/media.txt';m=json.loads(p.read_text('utf8'));m.update(openingFPS=6,openingFrames=663,openingAtlasSize=[1024,144]);p.write_text(json.dumps(m,separators=(',',':')),encoding='utf8')
test=(R/'tools/test-ui-v018.cjs').read_text('utf8').replace('ui-v018-tests.json','ui-v019-tests.json');(R/'tools/test-ui-v019.cjs').write_text(test,encoding='utf8')
native=(R/'tools/native-opening-v018.cjs').read_text('utf8').replace('v018','v019').replace('0.1.8','0.1.9');(R/'tools/native-opening-v019.cjs').write_text(native,encoding='utf8')
print('v0.1.9: six frames/sec, four-frame horizontal sheets, guarded changed-only writes')
