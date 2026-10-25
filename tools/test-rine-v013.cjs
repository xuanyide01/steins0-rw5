const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const R=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(R,p),'utf8'));
function load(name){let s=fs.readFileSync(path.join(R,'src/common',name+'.js'),'utf8'),names=[...s.matchAll(/export (?:function|const) (\w+)/g)].map(x=>x[1]);return vm.runInNewContext(s.replace(/export /g,'')+'\n;({'+names.join(',')+'})',{console,Number,Date,JSON,Object,Array,Error,Math});}
const e=load('engine'),c=load('conversations'),g=read('src/common/graph.txt');e.configure(g);let sent=0,expirations=0;
for(const [node,n] of Object.entries(g.nodes))for(const event of n.events)if(event.type==='rineReply'){
 const record=read('src/common/reply/'+event.key+'.txt');
 for(let i=0;i<record.replies.length;i++){
  let s=e.newState(node,true,event.at);e.locate(s);if(!s.replyWindows.some(w=>w.base===event.base))continue;
  const msg=s.inbox.find(m=>m.base===event.base),thread=c.threadForMessage(s,msg,false);assert.ok(c.canReply(s,thread));
  assert.equal(c.mailboxSummary(s),'有新信息');e.markRead(s);assert.match(c.mailboxSummary(s),/^\d+组-\d+条信息$/);
  const before=s.mailSequence,sequence=e.sendReply(s,record,i),original=record.replies[i];assert.equal(sequence.length,original.sequence.length+1);
  const first=s.sent.find(m=>m.order===before+1);assert.equal(first.id,original.id);assert.equal(first.stamp,record.stampChoices);assert.equal(first.sender,0);
  assert.equal(s.mailSequence-before,sequence.length);const actual=c.conversationMessages(s,thread).filter(m=>m.order>before).map(({sender,stamp,id})=>({sender,stamp,id}));
  assert.deepEqual(JSON.parse(JSON.stringify(actual)),[{sender:0,stamp:record.stampChoices,id:original.id},...original.sequence.map(({sender,stamp,id})=>({sender,stamp,id}))]);
  s=e.restore(e.checkpoint(s));assert.equal(c.canReply(s,thread),false);assert.throws(()=>e.sendReply(s,record,i));
  const expiration=n.events.find(x=>x.type==='expireRine'&&x.base===event.base&&x.at>=event.at);if(expiration){const length=s.inbox.length+s.sent.length;s.cursor=expiration.at;e.locate(s);assert.equal(s.inbox.length+s.sent.length,length,'Reply must suppress only the unchosen fallback');}
  sent++;
 }
}
for(const [node,n] of Object.entries(g.nodes))for(let i=0;i<n.events.length;i++){
 const ex=n.events[i];if(ex.type!=='expireRine')continue;
 for(const read of [false,true]){
  const s=e.newState(node,true,Math.max(0,ex.at-1));e.locate(s);if(read)e.markRead(s);const before=s.mailSequence;s.cursor=ex.at;e.locate(s);
  const actual=s.inbox.concat(s.sent).filter(m=>m.order>before&&m.base===ex.base).sort((a,b)=>a.order-b.order).map(({sender,stamp,id})=>({sender,stamp,id}));
  const expected=(read?ex.readMessages:n.events.slice(i+1).filter(m=>m.type==='message'&&m.at===ex.at&&m.base===ex.base)).map(({sender,stamp,id})=>({sender,stamp,id}));
  assert.deepEqual(JSON.parse(JSON.stringify(actual)),expected);assert.ok(!s.replyWindows.some(w=>w.base===ex.base));
 }
 expirations++;
}
const report={result:'passed',choiceWindowsExercised:sent,readAndUnreadExpirations:expirations,selectedOutgoingTextAndStickerRecorded:true,originalFollowupSequenceAndOrder:true,originalExpirationPreserved:true,noDuplicateFallbackAfterReply:true,mailboxUnreadAndCounts:true};
fs.writeFileSync(path.join(R,'reports/rine-tests-v013.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
