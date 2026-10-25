'use strict';
const {VM,ir}=require('./desktop-vm.cjs'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'reports/raw-story');fs.mkdirSync(dir,{recursive:true});
const out=path.join(root,'reports'),hash=x=>crypto.createHash('sha256').update(typeof x==='string'?x:JSON.stringify(x)).digest('hex'),copy=x=>JSON.parse(JSON.stringify(x));
const sourceTexts=JSON.parse(fs.readFileSync(path.resolve(root,'../steins0-probe/decoded-glyphs.json'),'utf8'));
const titles=Array.from({length:14},(_,i)=>sourceTexts.macrosys2[i*2+3].text),endings=[titles[5],titles[12],titles[11],titles[10],titles[9],titles[13]];
const queue=[],nodes={},memo=new Map(),visuals=[],vmap=new Map(),blockMap=new Map(),starts={};let frames=0,merged=0;
function stateKey(vm){
 const s=vm.s,t=s.threads[0],vars=Object.entries(s.vars).filter(([key])=>{const [g,n]=key.split(':');return g==='F'&&(Number(n)<1000||[2620,2740,2743,2749,2750].includes(Number(n)))||g==='W'&&[1025,6602,6604,6613].includes(Number(n));}).sort(([a],[b])=>a.localeCompare(b));
 return hash([t.script,t.pc,t.stack,s.banks[3],s.trueEndAvailable,vars,(s.phone.ignored||[]).map(x=>x.replace(/:\d+$/,''))]);
}
function enqueue(vm){const key=stateKey(vm);if(memo.has(key)){merged++;return memo.get(key);}const id='n'+memo.size;memo.set(key,id);nodes[id]={};queue.push({id,saved:vm.snapshot()});return id;}
function visual(vm){const t=vm.s.threads[0],rows=[[],[]];for(let k=0;k<2;k++)for(let slot=0;slot<8;slot++)if(vm.get(t,'F',(k?2410:2400)+slot))rows[k].push([slot,...Array.from({length:24},(_,j)=>vm.get(t,'W',(k?5100:4500)+40*slot+j))]);const key=JSON.stringify(rows);if(!vmap.has(key)){vmap.set(key,visuals.length);visuals.push(rows);}return vmap.get(key);}
function chunk(rows){const result=[];for(let i=0;i<rows.length;i+=80){const data=rows.slice(i,i+80),text=JSON.stringify(data),key=hash(text);let file=blockMap.get(key);if(!file){file=blockMap.size+'.txt';blockMap.set(key,file);fs.writeFileSync(path.join(dir,file),text);}result.push({file,count:data.length});}return result;}
const initial=enqueue(new VM());
for(let qi=0;qi<queue.length;qi++){
 if(qi>1500)throw Error('Graph exceeded audited state cap');const {id,saved}=queue[qi],vm=new VM(saved);vm.decisions=true;const node=nodes[id],rows=[],events=[];let first=true;
 for(let guard=0;guard<40000;guard++){
  const f=vm.next({tickLimit:10000}),t=vm.s.threads[0];
  for(const event of vm.s.events.splice(0)){
   // OP source cue is explicit: SG0_00_04 invokes macrosys2:8 with W61=16.
   if(event.type==='movie'){if(event.site.label==='12'&&event.id===16)events.push({at:rows.length,type:'opening'});continue;}
   events.push({at:rows.length,...event});
  }
  if(f.type==='text'){
   const group=vm.get(t,'W',4300),date=vm.get(t,'W',1029),name=titles[group]||'',source=ir.scripts[f.script].name;
   if(!starts[source])starts[source]={node:id,index:rows.length,name,script:f.script,date,group};
   const contacts=Array.from({length:10},(_,j)=>vm.get(t,'F',2700+j)?1<<j:0).reduce((a,b)=>a|b,0),rate=vm.get(t,'W',6701)||1129848;
   rows.push([f.speaker,f.text,visual(vm),date,name,f.site,vm.s.root,contacts,rate]);frames++;
  }else if(f.type==='choice'){
   if(![2,13,16,18].includes(f.mode)){vm.answer(f,false);continue;}
   const power=f.mode===18||f.mode===2,critical=power&&f.site.script==='SG0_01_08'||['SG0_A02_08','SG0_A03_11','SG0_B01_11'].includes(f.site.script);
   node.choice={kind:power?'power':'call',mode:f.mode,contact:f.contact,source:f.site,heading:power?'是否关闭手机电源？':f.mode===13?'Amadeus 来电':'来电',category:critical?'关键剧情操作':'一般电话',critical,items:[]};
   for(const yes of [true,false]){const child=new VM(vm.snapshot());child.answer(f,yes);node.choice.items.push({text:power?(yes?'关闭手机电源':'保持开机，继续剧情'):(yes?'接听电话':'暂不接听，继续剧情'),action:yes?'accept':'defer',to:enqueue(child)});}break;
  }else if(f.type==='condition'){
   node.condition={flag:f.condition,yes:null,no:null};for(const yes of [true,false]){const child=new VM(vm.snapshot());child.answer(f,yes);node.condition[yes?'yes':'no']=enqueue(child);}break;
  }else if(f.type==='end'){node.ending=endings[f.ending];node.endingId=f.ending;break;}
  else throw Error('Unexpected event '+f.type);
 }
 node.chunks=chunk(rows);node.count=rows.length;node.events=events;
 if(qi%20===0)console.log(JSON.stringify({node:id,queued:queue.length,frames,visuals:visuals.length,merged}));
 fs.writeFileSync(path.join(out,'graph-compile-progress.json'),JSON.stringify({processed:qi+1,queued:queue.length,frames,merged}));
}
const graph={format:3,initial,nodes,starts,titles,endings};fs.writeFileSync(path.join(out,'raw-graph.json'),JSON.stringify(graph));fs.writeFileSync(path.join(out,'raw-visuals.json'),JSON.stringify(visuals));
fs.writeFileSync(path.join(out,'graph-compile.json'),JSON.stringify({status:'compiled-awaiting-visual-and-route-replay-validation',nodes:queue.length,frames,visuals:visuals.length,blocks:blockMap.size,merged},null,2));
console.log('COMPILED',queue.length,frames,visuals.length,blockMap.size);
