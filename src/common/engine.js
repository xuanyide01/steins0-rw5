// Watch runtime: scene blocks, edges and phone events only. No original VM.
let graph=null;
const clone=x=>JSON.parse(JSON.stringify(x));
export function configure(data){if(!data||data.format!==3||!data.nodes[data.initial])throw Error('剧情目录无效');graph=data;}
export function getGraph(){return graph;}
// Original CLRFLG: normal clears set F801+id. Ending 5 additionally sets F804.
// Normalize both new settlements and legacy records; never infer from a title.
export function normalizeEndings(saved){const endings=Object.assign({},saved||{});if(endings[5])endings[3]=true;return endings;}
export function newState(id,story,cursor){return {format:3,chapter:id||graph.initial,cursor:cursor||0,progression:story===false?'chapter':'story',endings:{},inbox:[],sent:[],mailSequence:0,replyWindows:[],replied:[],read:[],eventNode:'',eventIndex:0,pendingCall:null,choice:null,history:[],speaker:'',text:'',title:'',date:'',group:-1,contacts:0,worldline:1129848,lastCard:-1,openingDone:!!(id&&id!==graph.initial)||Number(cursor)>=934};}
export function newChapterState(item){return newState(item.node,false,item.index);}
export function checkpoint(s){const out=Object.assign({},s);delete out.history;delete out.sceneLayers;return clone(out);}
export function restore(saved,owned){if(!saved||saved.format!==3||!graph.nodes[saved.chapter]||!Number.isInteger(saved.cursor)||saved.cursor<0||saved.cursor>graph.nodes[saved.chapter].count||!Array.isArray(saved.inbox)||saved.inbox.length>1200)throw Error('存档位置无效');const state=Object.assign(newState(),owned?saved:clone(saved),{history:[]});state.endings=normalizeEndings(state.endings);if(typeof saved.openingDone!=='boolean')state.openingDone=state.chapter!==graph.initial||state.cursor>=934;let order=state.mailSequence||0;for(const list of [state.inbox,state.sent]){let base=0;for(const m of list){if(!m.stamp)base=Math.floor(m.id/256)*256;if(typeof m.base!=='number')m.base=base;if(m.date===undefined)m.date=Number(state.date)||0;if(m.order===undefined)m.order=++order;else order=Math.max(order,m.order);}}state.mailSequence=order;return state;}
function remember(s){s.history.push(checkpoint(s));if(s.history.length>8)s.history.shift();}
function receive(s,e,delivery){const list=e.outgoing?s.sent:s.inbox,base=e.base===undefined?Math.floor(e.id/256)*256:e.base,key=delivery||e.contact+':'+e.id+':'+(e.stamp?1:0);if(list.some(x=>x.key===key))return;s.mailSequence=(s.mailSequence||0)+1;list.push({key,id:e.id,base,date:e.date===undefined?Number(s.date)||0:e.date,order:s.mailSequence,contact:e.contact,sender:e.sender===undefined?e.contact:e.sender,stamp:!!e.stamp,outgoing:!!e.outgoing});}
function events(s){
 const fallback={};const node=graph.nodes[s.chapter];if(s.eventNode!==s.chapter){s.eventNode=s.chapter;s.eventIndex=0;}
 while(s.eventIndex<node.events.length&&node.events[s.eventIndex].at<=s.cursor){const e=node.events[s.eventIndex++];
  if(e.type==='closeChoice')s.pendingCall=null;
  else if(e.type==='rineReset'){s.replyWindows=[];if(e.scope!=='display'){s.inbox=[];s.sent=[];s.replied=[];s.read=[];s.mailSequence=0;}}
  else if(e.type==='rineReply'){s.replyWindows=s.replyWindows.filter(x=>x.base!==e.base);s.replyWindows.push(clone(e));}
  else if(e.type==='expireRine'){s.replyWindows=s.replyWindows.filter(x=>x.base!==e.base);if(e.readMessages&&s.replied.indexOf(e.base)<0&&s.inbox.some(m=>m.base===e.base&&s.read.indexOf(m.key)>=0)){fallback[e.at+':'+e.base]=true;e.readMessages.forEach((m,i)=>receive(s,Object.assign({},m,{base:e.base}),'f:'+s.chapter+':'+(s.eventIndex-1)+':'+i));}}
  else if(e.type==='message'&&!fallback[e.at+':'+e.base]&&s.replied.indexOf(e.base===undefined?Math.floor(e.id/256)*256:e.base)<0)receive(s,e,'s:'+s.chapter+':'+(s.eventIndex-1));
 }
}
function move(s,id){s.chapter=id;s.cursor=0;s.choice=null;s.eventNode='';s.eventIndex=0;}
export function locate(s){
 if(s.choice)return {type:'choice',...s.choice};
 for(let guard=0;guard<30;guard++){
  events(s);const node=graph.nodes[s.chapter];
  if(s.cursor<node.count){let base=0;for(const part of node.chunks){if(s.cursor<base+part.count)return {type:'text',file:part.file,base};base+=part.count;}throw Error('剧情分块索引无效');}
  if(node.condition){move(s,node.condition[s.endings[0]?'yes':'no']);continue;}
  if(node.choice){if(node.choice.critical){s.choice=clone(node.choice);return {type:'choice',...s.choice};}s.pendingCall=clone(node.choice);move(s,node.choice.items[1].to);continue;}
  if(node.endingId===undefined)throw Error('剧情连接缺失');s.ended=true;s.endingName=node.ending;s.endingId=node.endingId;s.endings[node.endingId]=true;s.endings=normalizeEndings(s.endings);return {type:'end',ending:node.ending};
 }
 throw Error('剧情连接次数过多');
}
export function readFrame(chunk,s,base){const f=locate(s);if(f.type!=='text')return f;const row=chunk.frames[s.cursor-base];if(!row)return {type:'yield'};s.speaker=row[0];s.text=row[1];s.date=row[3];s.group=row[4];s.title=graph.titles[row[4]]||'';s.sourceSite=row[5];s.sourceScript=row[6];s.contacts=row[7];s.worldline=row[8];s.sceneLayers=chunk.views[row[2]];return {type:'text',speaker:s.speaker,text:s.text};}
export function next(s){if(locate(s).type!=='text')return;remember(s);s.cursor++;}
export function choose(s,item,index){const f=locate(s);if(f.type!=='choice'||!f.items[index]||f.items[index].to!==item.to)throw Error('当前选项已变化');remember(s);const choice=s.choice;s.choice=null;s.pendingCall=index===1&&!choice.late?clone(choice):null;if(!choice.late||index===0)move(s,item.to);}
export function phoneChoice(s){return s.choice||s.pendingCall;}
export function answerCall(s,accept){const c=phoneChoice(s);if(!c)return false;if(s.choice){choose(s,c.items[accept?0:1],accept?0:1);return true;}if(accept){remember(s);s.pendingCall=null;move(s,c.items[0].to);}return true;}
function groupAt(node,cursor){let group=-1;for(const row of node.chapters||[]){if(row[0]>cursor)break;group=row[1];}return group;}
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
}
export function previous(s){const old=s.history.pop();if(!old)return false;const history=s.history;Object.assign(s,restore(old),{history});return true;}
export function markRead(s){s.read=s.inbox.map(x=>x.key);}
export function sendReply(s,record,index){const window=s.replyWindows.find(x=>x.base===record.base);if(!window||s.replied.indexOf(record.base)>=0)throw Error('这条消息已过回复时机');const reply=record.replies[index];if(!reply)throw Error('回复选项无效');const received=s.inbox.filter(m=>m.base===record.base),date=received.length?received[received.length-1].date:Number(s.date)||0;const sequence=[{id:reply.id,sender:0,outgoing:true,stamp:!!record.stampChoices,contact:record.contact}].concat(reply.sequence);sequence.forEach((row,i)=>receive(s,Object.assign({},row,{base:record.base,date}),'r:'+record.base+':'+index+':'+(i===0?'selected':i-1)));s.replied.push(record.base);s.replyWindows=s.replyWindows.filter(x=>x.base!==record.base);return sequence;}
export function chapterTitle(s){return s.title||'章节开头';}
export function storyDate(s){const d=Number(s.date)||0,m=Math.floor(d/100)%100,day=d%100;return m>=1&&m<=12&&day>=1&&day<=31?'（日期：'+('0'+m).slice(-2)+'.'+('0'+day).slice(-2)+'）':'（日期：？？.？？）';}

// Only acknowledge incoming messages in a successfully rendered page.
export function markMessagesRead(s,messages){for(const m of messages){if(!m.outgoing&&s.inbox.some(x=>x.key===m.key)&&s.read.indexOf(m.key)<0)s.read.push(m.key);}}
