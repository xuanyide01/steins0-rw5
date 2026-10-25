from pathlib import Path
import json,shutil
from fontTools.ttLib import TTFont
R=Path(__file__).resolve().parents[1];O=R/'src/common'
font=TTFont(O/'sg-original.ttf');baselinePath=R/'reports/before-v012/sg-original.ttf';baseline=TTFont(baselinePath) if baselinePath.exists() else font;changed=0
for name,(advance,lsb) in list(font['hmtx'].metrics.items()):
    actual=getattr(font['glyf'][name],'xMin',0)
    if actual!=baseline['hmtx'].metrics[name][1]:changed+=1
    font['hmtx'].metrics[name]=(advance,actual)
font['head'].flags|=2
font.save(O/'sg-original.ttf')
a=json.loads((O/'assets.txt').read_text('utf8'));replacement={};audit=[]
for old,geo in a['portraitGeometry'].items():
    name=geo['source'];face=old.split('_')[-1]
    if name not in ['DAR_AMA.png','DAR_AMB.png','DAR_ASA.png']:continue
    target='DAR_DSC.png' if name=='DAR_ASA.png' else 'DAR_DMC.png'
    found=[k for k,v in a['portraitGeometry'].items() if v['source']==target and k.endswith('_'+face)]
    assert len(found)==1,(old,target,face)
    new=found[0];g=a['portraitGeometry'][new];replacement[old]={'key':new,'ratio':g['size'][0]/g['size'][1]}
    audit.append({'from':name,'fromKey':old,'to':target,'toKey':new,'sameExpressionId':True})
digital=[k for k,v in a['portraitGeometry'].items() if v['source'].startswith('CRS_J')]
module='''// Original SG0 resources only. Keep existing scene placement and body baseline.
const replacements=REPLACEMENTS;
const digitalPortraits=DIGITAL;
export function presentedLayer(v){const r=replacements[v[0]];if(!r)return v;const width=Math.round(v[4]*r.ratio);return [r.key,Math.round(v[1]+v[3]/2-width/2),v[2],width,v[4],v[5]];}
export function amadeusImage(speaker,layers){if(String(speaker||'').indexOf('Amadeus')<0||(layers||[]).some(v=>digitalPortraits.indexOf(v[0])>=0))return '';return 'p120_1';}
'''.replace('REPLACEMENTS',json.dumps(replacement,separators=(',',':'))).replace('DIGITAL',json.dumps(digital,separators=(',',':')))
assert 'p120_1' in a['portraitGeometry'] and a['portraitGeometry']['p120_1']['source']=='CRS_JMD.png'
(O/'scene-presentation.js').write_text(module,encoding='utf8')
for file in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/file;x=json.loads(p.read_text('utf8'))
    if file=='package.json':x['version']='0.1.2'
    else:x['versionName']='0.1.2';x['versionCode']=6
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'reports/presentation-v012.json').write_text(json.dumps({'fontCorrectedSideBearings':changed,'advancesUnchanged':True,'legacyDaruReplacements':audit,'amadeusOriginalAsset':'CRS_JMD.png / p120_1','source':'STEINS;GATE 0/USRDIR/chara.mpk'},ensure_ascii=False,indent=2),encoding='utf8')
print(changed,'font bearings;',len(audit),'Daru replacements')
