from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v016';B.mkdir(exist_ok=True)
for name in ['src/pages/index/index.ux','src/common/engine.js','src/common/graph.txt','src/common/assets.js']:
    p=B/name;p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():shutil.copyfile(R/name,p)
p=R/'src/common/graph.txt';g=json.loads((B/'src/common/graph.txt').read_text('utf8'))
for n in g['nodes'].values():
    at=0;previous=None;chapters=[]
    for part in n['chunks']:
        for row in json.loads((R/'src/common/story'/part['file']).read_text('utf8'))['frames']:
            if row[4]!=previous:chapters.append([at,row[4]]);previous=row[4]
            at+=1
    assert at==n['count'];n['chapters']=chapters
p.write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')),encoding='utf8')
p=R/'src/common/engine.js';s=(B/'src/common/engine.js').read_text('utf8');start=s.index('export function nextChapter(s)');end=s.index('\nexport function previous',start)
s=s[:start]+'''function groupAt(node,cursor){let group=-1;for(const row of node.chapters||[]){if(row[0]>cursor)break;group=row[1];}return group;}
export function nextChapter(s){
 if(locate(s).type!=='text')return false;remember(s);
 const initial=groupAt(graph.nodes[s.chapter],s.cursor);
 for(let guard=0;guard<200;guard++){
  const place=locate(s);if(place.type!=='text')return true;
  const node=graph.nodes[s.chapter];if(groupAt(node,s.cursor)!==initial)return true;
  let at=node.count;for(const row of node.chapters||[])if(row[0]>s.cursor&&row[1]!==initial){at=row[0];break;}
  if(s.pendingCall&&s.pendingCall.critical){const close=node.events.find(e=>e.type==='closeChoice'&&e.at>s.cursor);if(close&&close.at<=at){s.cursor=close.at;s.choice=Object.assign(clone(s.pendingCall),{late:true});return true;}}
  const important=node.events.find(e=>e.at>s.cursor&&e.at<=at&&e.critical&&(e.type==='message'||e.type==='rineReply'));
  if(important){s.cursor=important.at;return true;}
  s.cursor=at;
 }
 throw Error('跳章连接次数过多');
}'''+s[end:];p.write_text(s,encoding='utf8')
p=R/'src/pages/index/index.ux';s=(B/'src/pages/index/index.ux').read_text('utf8')
s=s.replace('import {imagePath}', 'import {imagePath,imagePaths}')
old="this.sceneImages=(this._state.sceneLayers||[]).map(presentedLayer).map((v,i)=>({key:i+':'+v[0],src:imagePath(v[0]),left:v[1],top:v[2],width:v[3],height:v[4],opacity:v[5]/1000}));"
new="const specs=(this._state.sceneLayers||[]).map(presentedLayer),signature=JSON.stringify(specs);if(signature!==this._sceneSignature){this._sceneSignature=signature;this._sceneEpoch=(this._sceneEpoch||0)+1;this.sceneImages=specs.reduce((out,v,i)=>{const files=imagePaths(v[0]);files.forEach((src,j)=>out.push({key:this._sceneEpoch+':'+i+':'+j,group:i,ready:false,src,left:v[1],top:v[2],width:v[3],height:v[4],targetOpacity:v[5]/1000,opacity:files.length>1?0:v[5]/1000}));return out;},[]);}"
assert old in s;s=s.replace(old,new)
s=s.replace('class="layer" src="{{$item.src}}"', 'class="layer" src="{{$item.src}}" oncomplete="sceneLayerLoaded($item.key)" onerror="sceneLayerFailed($item.key)"')
s=s.replace(' startText(){', ''' sceneLayerLoaded(key){const item=this.sceneImages.find(x=>x.key===key);if(!item||item.ready)return;item.ready=true;const group=this.sceneImages.filter(x=>x.group===item.group);if(group.every(x=>x.ready))for(const row of group)row.opacity=row.targetOpacity;},
 sceneLayerFailed(key){if(this.mode==='play'&&this.sceneImages.some(x=>x.key===key))this.fail('场景图片读取失败，请重启后读取存档重试');},
 startText(){''')
s=s.replace('this.sceneImages=[];this.lines=[];', "this.sceneImages=[];this._sceneSignature='';this.lines=[];")
s=s.replace('.title-rule{position:absolute;left:42px;top:470px;width:348px;', '.title-rule{position:absolute;left:64px;top:466px;width:304px;')
s=s.replace('.motto{position:absolute;left:42px;top:480px;font-size:15px;', '.motto{position:absolute;left:64px;top:476px;width:304px;height:22px;font-size:15px;')
s=s.replace("const messages=conversationMessages(this._state,thread),pages=Math.max(1,Math.ceil(messages.length/8));this._threadPage=Math.max(0,Math.min(pages-1,this._threadPage||0));", "const messages=conversationMessages(this._state,thread);this._threadPage=0;")
s=s.replace('const current=messages.slice(this._threadPage*8,this._threadPage*8+8),parts=[];let i=0;', 'const current=messages,parts=[];let i=0;')
s=s.replace("messages.length+' 条消息 · '+pageLabel(this._threadPage,pages)", "messages.length+' 条消息 · 上下滑动查看'")
s=s.replace("this.phoneLeftLabel=this._threadPage>0?'‹ 较早消息':'';this.phoneRightLabel=this._threadPage<pages-1?'较新消息 ›':canReply(this._state,thread)?'回复':'继续剧情';", "this.phoneLeftLabel='';this.phoneRightLabel=canReply(this._state,thread)?'回复':'继续剧情';")
s=s.replace("const before=conversationMessages(this._state,this._thread).length;sendReply", "sendReply")
s=s.replace('this._threadPage=Math.floor(before/8);', 'this._threadPage=0;')
s=s.replace("if(this._thread&&this._threadPage>0){this._threadPage--;this.renderThread();}return;", 'return;')
s=s.replace("if(this._thread&&this._threadPage<Math.ceil(conversationMessages(this._state,this._thread).length/8)-1){this._threadPage++;this.renderThread();}else if(this._thread&&canReply(this._state,this._thread))", "if(this._thread&&canReply(this._state,this._thread))")
p.write_text(s,encoding='utf8')
for file in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/file;obj=json.loads(p.read_text('utf8'))
    if file=='package.json':obj['version']='0.1.6';obj['scripts']['test']=obj['scripts']['test'].replace('test-ui-v015','test-ui-v016')
    else:obj['versionName']='0.1.6';obj['versionCode']=10
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('v0.1.6 chapter boundaries, footer safe area, single-page conversation')
