// Read original SC3 instructions/tables; verify every exported choice and branch.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{VM,ir}=require('./desktop-vm.cjs');
const R=path.resolve(__dirname,'..'),file=path.join(R,'src/common/graph.txt'),g=JSON.parse(fs.readFileSync(file)),source=ir.scripts[1];
function evaluate(base,callback,action){
 const m=new VM(),t=m.s.threads[0];m.put(t,'W',6655,base);m.put(t,'W',1502,(callback-24)/10);m.s.phone.contact=0;m.jump(t,1,action);t.stack=[];
 const rows=[];
 for(let i=0;i<1200;i++){
  if(t.script===1&&source.siteLabels[t.pc]==='14')return rows;
  const op=ir.scripts[t.script].ops[t.pc];if(op[0]==='SG0Phone2E')rows.push({contact:0,sender:m.val(op[1],t),outgoing:m.val(op[1],t)===0,stamp:!!m.val(op[2],t),id:m.val(op[3],t)});
  m.step(t);
 }throw Error('Source branch did not finish');
}
const records=new Map(),results=[];
for(const n of Object.values(g.nodes))for(const e of n.events)if(e.type==='rineReply'&&!records.has(e.base)){
 const r=JSON.parse(fs.readFileSync(path.join(R,'src/common/reply',e.key+'.txt'))),callback=+e.key.split('-')[1];
 const ops=source.ops.slice(source.labels[callback],source.labels[callback+1]);
 const choices=ops.filter(o=>o[0]==='SG0Phone0D');assert.equal(choices.length,r.replies.length);
 const m=new VM(),t=m.s.threads[0];m.put(t,'W',6655,e.base);
 for(let i=0;i<choices.length;i++){
  const o=choices[i],reply=r.replies[i];assert.equal(m.val(o[1],t),reply.id);m.jump(t,1,m.val(o[2],t));const rows=[];
  for(let guard=0;guard<1200;guard++){const op=source.ops[t.pc];if(op[0]==='SG0Phone0B')break;assert.ok(['SG0Phone0F','SetFlag'].includes(op[0]));if(op[0]==='SG0Phone0F')rows.push({sender:m.val(op[1],t),outgoing:m.val(op[1],t)===0,stamp:!!m.val(op[2],t),id:m.val(op[3],t),contact:r.contact});m.step(t);}
  assert.deepEqual(reply.sequence,rows);
 }
 const read=evaluate(e.base,callback,8),unread=evaluate(e.base,callback,9);records.set(e.base,{read,unread});results.push({base:e.base,key:e.key,choices:choices.length,read,unread});
}
let sites=0;
for(const n of Object.values(g.nodes))for(let i=0;i<n.events.length;i++){
 const e=n.events[i];if(e.type!=='expireRine')continue;const r=records.get(e.base);assert.ok(r);
 const fallback=n.events.slice(i+1).filter(m=>m.at===e.at&&m.type==='message'&&m.base===e.base).map(({contact,sender,outgoing,stamp,id})=>({contact,sender,outgoing,stamp,id}));
 assert.deepEqual(fallback,r.unread,'Compiled no-read fallback must equal the original table');const date=n.events.slice(i+1).find(m=>m.at===e.at&&m.type==='message'&&m.base===e.base)?.date;e.readMessages=r.read.map(m=>date===undefined?m:{...m,date});sites++;
}
g.phone.replyBases=[...records.keys()];fs.writeFileSync(file,JSON.stringify(g));
const report={result:'passed',source:'Original _rndrine SC3 SG0Phone0D/0F and table17 read/unread branches',sets:results.length,choices:results.reduce((n,r)=>n+r.choices,0),expirationSites:sites,selectedMessageAddedAtSend:true,results};
fs.writeFileSync(path.join(R,'reports/rine-audit-v013.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({...report,results:undefined}));
