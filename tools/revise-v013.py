from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v013';B.mkdir(exist_ok=True)
for f in ['src/pages/index/index.ux','src/common/engine.js','src/common/conversations.js','src/common/graph.txt','src/common/assets.js']:
    p=B/Path(f).name
    if not p.exists():shutil.copyfile(R/f,p)
p=R/'src/common/conversations.js';s=p.read_text('utf8')
if 'mailboxSummary' not in s:s+='''\nexport function mailboxSummary(state){return state.inbox.some(m=>state.read.indexOf(m.key)<0)?'有新信息':mailboxThreads(state,false).length+'组-'+state.inbox.length+'条信息';}
export function canReply(state,thread){return state.replied.indexOf(thread.base)<0&&state.replyWindows.some(w=>w.base===thread.base);}
'''
p.write_text(s,encoding='utf8')
p=R/'src/pages/index/index.ux';s=(B/'index.ux').read_text('utf8')
s=s.replace('threadForMessage,mailDateLabel}', 'threadForMessage,mailDateLabel,mailboxSummary,canReply}')
s=s.replace("meta:mailboxThreads(this._state,false).length+' 组 · '+this._state.inbox.length+' 条消息'",'meta:mailboxSummary(this._state)')
s=s.replace("(t.latest.stamp?' · 动画表情':' · 点击查看')", "(canReply(this._state,t)?' · 可回复':t.latest.stamp?' · 动画表情':' · 点击查看')")
s=s.replace("items=record.replies.map((r,i)=>({text:record.stampChoices?", "items=record.replies.map((r,i)=>({image:record.stampChoices?'/common/phone-stamps/'+r.id+'.png':'',text:record.stampChoices?")
s=s.replace("text,font:textFont(text),meta:", "text,image:x.image||'',font:textFont(text),meta:")
s=s.replace('height:Math.max(73,titleHeight+36)',"height:x.image?162:Math.max(73,titleHeight+36)")
s=s.replace("if(i>=current.length){\n    this.showPhoneDetail", "if(i>=current.length){\n    if(!canReply(this._state,thread)){const replied=this._state.replied.indexOf(thread.base)>=0,wasReply=(this._graph.phone.replyBases||[]).indexOf(thread.base)>=0;parts.push({kind:'label',text:replied?'已回复':wasReply?'此条消息已过原作回复时机':'此段对话没有回复选项'});}\n    this.showPhoneDetail")
s=s.replace("this._state.replyWindows.some(x=>x.base===thread.base)?'回复':''", "canReply(this._state,thread)?'回复':''")
s=s.replace("this._threadPage<pages-1?'较新消息 ›':'继续剧情'", "this._threadPage<pages-1?'较新消息 ›':canReply(this._state,thread)?'回复':'继续剧情'")
s=s.replace("}else this.resume();return;}if(this._phonePage", "}else if(this._thread&&canReply(this._state,this._thread))this.replyMessage();else this.resume();return;}if(this._phonePage")
# Original sticker choices are images too, so choosing a response is meaningful.
needle='<text class="phone-row-title"'
if needle in s:s=s.replace(needle,'<image if="{{$item.image}}" class="reply-stamp" src="{{$item.image}}"></image>'+needle)
s=s.replace('</style>', '.reply-stamp{width:110px;height:86px;object-fit:contain;}\n</style>')
p.write_text(s,encoding='utf8')
p=R/'src/common/engine.js';s=(B/'engine.js').read_text('utf8')
s=s.replace("const node=graph.nodes[s.chapter];if(s.eventNode", "const fallback={};const node=graph.nodes[s.chapter];if(s.eventNode")
s=s.replace("else if(e.type==='expireRine')s.replyWindows=s.replyWindows.filter(x=>x.base!==e.base);", "else if(e.type==='expireRine'){s.replyWindows=s.replyWindows.filter(x=>x.base!==e.base);if(e.readMessages&&s.replied.indexOf(e.base)<0&&s.inbox.some(m=>m.base===e.base&&s.read.indexOf(m.key)>=0)){fallback[e.at+':'+e.base]=true;e.readMessages.forEach((m,i)=>receive(s,Object.assign({},m,{base:e.base}),'f:'+s.chapter+':'+(s.eventIndex-1)+':'+i));}}")
s=s.replace("else if(e.type==='message'&&s.replied", "else if(e.type==='message'&&!fallback[e.at+':'+e.base]&&s.replied")
s=s.replace("reply.sequence.forEach((row,i)=>receive(s,Object.assign({},row,{base:record.base}),'r:'+record.base+':'+index+':'+i));", "const sequence=[{id:reply.id,sender:0,outgoing:true,stamp:!!record.stampChoices,contact:record.contact}].concat(reply.sequence);sequence.forEach((row,i)=>receive(s,Object.assign({},row,{base:record.base}),'r:'+record.base+':'+index+':'+(i===0?'selected':i-1)));")
s=s.replace('return reply.sequence;', 'return sequence;')
s=s.replace("const sequence=[", "const received=s.inbox.filter(m=>m.base===record.base),date=received.length?received[received.length-1].date:Number(s.date)||0;const sequence=[")
s=s.replace("Object.assign({},row,{base:record.base})", "Object.assign({},row,{base:record.base,date})")
p.write_text(s,encoding='utf8')
for file in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/file;x=json.loads(p.read_text('utf8'))
    if file=='package.json':x['version']='0.1.3';x['scripts']['test']=x['scripts']['test'].replace('test-ui-v012','test-ui-v013')
    else:x['versionName']='0.1.3';x['versionCode']=7
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Revised v0.1.3 UI and runtime')
