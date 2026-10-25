from pathlib import Path
import json,shutil,re
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v014';B.mkdir(exist_ok=True)
for name in ['src/common/engine.js','src/common/scene-presentation.js','src/pages/index/index.ux']:
    p=B/name;p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():shutil.copyfile(R/name,p)
p=R/'src/common/engine.js';s=(B/'src/common/engine.js').read_text('utf8')
s+='''\n// Only acknowledge incoming messages in a successfully rendered page.
export function markMessagesRead(s,messages){for(const m of messages){if(!m.outgoing&&s.inbox.some(x=>x.key===m.key)&&s.read.indexOf(m.key)<0)s.read.push(m.key);}}
''';p.write_text(s,encoding='utf8')
p=R/'src/pages/index/index.ux';s=(B/'src/pages/index/index.ux').read_text('utf8').replace('previous,markRead,sendReply,','previous,markRead,markMessagesRead,sendReply,')
needle="this.showPhoneDetail(thread.sent?'已发送':'RINE',this.contactName(this.threadPeer(thread)),mailDateLabel(thread.date)+' · '+messages.length+' 条消息 · '+pageLabel(this._threadPage,pages),parts);"
assert needle in s;s=s.replace(needle,needle+"\n    markMessagesRead(this._state,current);console.log('STEINS0_RW5 thread-read '+thread.base+' '+this._threadPage+' '+this._state.read.length);")
p.write_text(s,encoding='utf8')
p=R/'src/common/scene-presentation.js';s=(B/'src/common/scene-presentation.js').read_text('utf8')
s=re.sub(r'const replacements=.*?;\n','',s);s=re.sub(r'export function presentedLayer\(v\)\{[^\n]+\}', 'export function presentedLayer(v){return v;}',s)
s=s.replace('Original SG0 resources only. Keep existing scene placement and body baseline.','Use the exact portrait/pose and placement chosen by the original SG0 script.')
p.write_text(s,encoding='utf8')
for file in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/file;obj=json.loads(p.read_text('utf8'))
    if file=='package.json':obj['version']='0.1.4';obj['scripts']['test']=obj['scripts']['test'].replace('test-ui-v013','test-ui-v014')
    else:obj['versionName']='0.1.4';obj['versionCode']=8
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Revised v0.1.4; original script costumes and per-page read acknowledgement')
