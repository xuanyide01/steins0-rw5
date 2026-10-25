const fs=require('fs'),path=require('path'),crypto=require('crypto'),{VM}=require('./desktop-vm.cjs');
const r=path.resolve(__dirname,'..'),g=JSON.parse(fs.readFileSync(path.join(r,'reports/raw-graph.json'))),results=[];
const recipe=(route,source,mode)=>['TA','RMG','PR'].includes(route)&&source==='SG0_01_08'&&mode===18||['RMG','PR'].includes(route)&&source==='SG0_A02_08'&&[13,16].includes(mode)||route==='PR'&&source==='SG0_A03_11'&&[13,16].includes(mode)||route==='GS'&&source==='SG0_B01_11'&&mode===13;
for(const route of ['TA','RMG','PR','GS','VA','TRUE']){
 const vm=new VM();vm.decisions=true;const h=()=>crypto.createHash('sha256'),expected=h(),actual=h();let count=0,graphCount=0,end;
 for(let i=0;i<50000;i++){const f=vm.next({tickLimit:10000});if(f.type==='choice')vm.answer(f,recipe(route,f.site.script,f.mode));else if(f.type==='condition')vm.answer(f,route==='TRUE');else if(f.type==='text'){expected.update(JSON.stringify([f.site,f.speaker,f.text,vm.s.vars['W:1029'],vm.s.vars['W:4300']||0]));count++;}else if(f.type==='end'){end=f.ending;break;}}
 let id=g.initial,graphEnd;for(let step=0;step<200;step++){
  const n=g.nodes[id];for(const c of n.chunks)for(const row of JSON.parse(fs.readFileSync(path.join(r,'reports/raw-story',c.file)))){actual.update(JSON.stringify([row[5],row[0],row[1],row[3],g.titles.indexOf(row[4])]));graphCount++;}
  if(n.choice)id=n.choice.items[recipe(route,n.choice.source.script,n.choice.mode)?0:1].to;
  else if(n.condition)id=n.condition[route==='TRUE'?'yes':'no'];else{graphEnd=n.endingId;break;}
 }
 const e=expected.digest('hex'),a=actual.digest('hex'),result=e===a&&count===graphCount&&end===graphEnd;
 results.push({route,result:result?'passed':'failed',referenceFrames:count,graphFrames:graphCount,referenceEnding:end,graphEnding:graphEnd,referenceHash:e,graphHash:a});console.log(JSON.stringify(results.at(-1)));
}
const views=JSON.parse(fs.readFileSync(path.join(r,'reports/raw-visuals.json'))),bg=new Set(),ch=new Set();for(const view of views){for(const row of view[0])bg.add(row[8]);for(const row of view[1])ch.add(row[10]+':'+row[13]);}
fs.writeFileSync(path.join(r,'reports/used-assets.json'),JSON.stringify({backgrounds:[...bg].sort((a,b)=>a-b),portraits:[...ch].sort()},null,2));
fs.writeFileSync(path.join(r,'reports/graph-replay.json'),JSON.stringify({status:results.every(r=>r.result==='passed')?'passed':'failed',method:'Independent walkthrough recipes replayed against desktop SC3 executor and compiled scene graph; speaker/text/source/date/chapter digest and ending compared.',guide:'https://sonome.dareno.me/projects/sg0-walkthrough.html',results,assets:{backgrounds:bg.size,portraits:ch.size}},null,2));
if(results.some(r=>r.result!=='passed'))process.exitCode=1;
