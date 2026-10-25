from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v015';B.mkdir(exist_ok=True)
for name in ['src/pages/index/index.ux','src/common/logo.png']:
    p=B/name;p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():shutil.copyfile(R/name,p)
p=R/'src/pages/index/index.ux';s=(B/'src/pages/index/index.ux').read_text('utf8')
s=s.replace("import {FONT_SIZES", "import {planTextRows,revealTextRows,nextGlyphEnd} from '../../common/text-reveal.js';\nimport {FONT_SIZES")
s=s.replace('clearInterval(this._typeTimer)','clearTimeout(this._typeTimer)')
s=s.replace("const mode=this._settings.textMode;this._sentenceStops", "const plan=planTextRows(this._wrapped,++this._ui);this._textRanges=plan.ranges;this.lines=plan.rows;\n  const mode=this._settings.textMode;this._sentenceStops")
start=s.index('  const token=this._typeGeneration,start=Date.now();');end=s.index('\n },',start)
s=s[:start]+'''  const token=this._typeGeneration;this.paintText('');if(!this._visible)return;
  const tick=()=>{
   if(token!==this._typeGeneration||this.mode!=='play'||!this._visible)return;
   this._typeTimer=null;this._typed=nextGlyphEnd(this._wrapped,this._typed);this.paintText(this._wrapped.slice(0,this._typed));
   if(this._typed<this._wrapped.length)this._typeTimer=setTimeout(tick,30);else this.armAuto();
  };
  if(this._wrapped.length)this._typeTimer=setTimeout(tick,30);else this.armAuto();'''+s[end:]
old="paintText(text){const uid=++this._ui;this.lines=text.split('\\n').map((text,i)=>({id:uid+':'+i,text}));}"
assert old in s;s=s.replace(old,"paintText(text){revealTextRows(this.lines,this._textRanges,text.length);}")
s=s.replace("if(this._typeTimer){clearTimeout(this._typeTimer);this._typeTimer=null;this._typed", "if(this._typeTimer){clearTimeout(this._typeTimer);this._typeTimer=null;this._typeGeneration++;this._typed")
s=s.replace('.line{width:384px;line-height:34px;', '.line{width:384px;height:34px;line-height:34px;')
p.write_text(s,encoding='utf8')
for file in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/file;x=json.loads(p.read_text('utf8'))
    if file=='package.json':x['version']='0.1.5';x['scripts']['test']=x['scripts']['test'].replace('test-ui-v014','test-ui-v015')
    else:x['versionName']='0.1.5';x['versionCode']=9
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Revised text reveal for v0.1.5')
