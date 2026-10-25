// Independent route recipes from the Committee of Zero's published walkthrough;
// destinations and ending IDs are obtained by executing original SC3 branches.
const {VM,ir}=require('./desktop-vm.cjs'),fs=require('fs'),path=require('path');
const output=path.resolve(__dirname,'../reports'),results=[];
for(const route of ['TA','RMG','PR','GS','VA','TRUE']){
 const vm=new VM();vm.decisions=true;let count=0,end=null,failure=null;const choices=[],scripts=[],assets={backgrounds:new Set(),portraits:new Set()};
 try{for(let i=0;i<50000;i++){
  const f=vm.next({tickLimit:10000});
  if(f.type==='choice'){
   let yes=false;
   if(['TA','RMG','PR'].includes(route))yes=f.site.script==='SG0_01_08'&&f.mode===18;
   if(['RMG','PR'].includes(route))yes||=f.site.script==='SG0_A02_08'&&[13,16].includes(f.mode);
   if(route==='PR')yes||=f.site.script==='SG0_A03_11'&&[13,16].includes(f.mode);
   if(route==='GS')yes=f.site.script==='SG0_B01_11'&&f.mode===13;
   choices.push({...f,answer:yes});vm.answer(f,yes);
  }else if(f.type==='condition')vm.answer(f,route==='TRUE');
  else if(f.type==='end'){end=f;break;}
  else if(f.type==='text'){
   count++;if(!scripts.includes(f.script))scripts.push(f.script);
   const t=vm.s.threads[0];for(let slot=0;slot<8;slot++){
    if(vm.get(t,'F',2400+slot))assets.backgrounds.add(vm.get(t,'W',4507+40*slot));
    if(vm.get(t,'F',2410+slot))assets.portraits.add(vm.get(t,'W',5109+40*slot)+':'+vm.get(t,'W',5112+40*slot));
   }
  }else throw Error('Unexpected event '+f.type);
 }}catch(e){failure={message:e.message,trace:vm.trace};}
 const row={route,result:failure?'blocked':'traced',count,end,choices,scripts:scripts.map(id=>ir.scripts[id].name),assets:Object.fromEntries(Object.entries(assets).map(([k,v])=>[k,[...v]])),failure,instructions:vm.stats.instructions};results.push(row);
 console.log(JSON.stringify({route,result:row.result,count,end,failure:failure?.message}));
 fs.writeFileSync(path.join(output,'route-audit.json'),JSON.stringify({status:'desktop-reference-only-not-a-validated-port',guide:'https://sonome.dareno.me/projects/sg0-walkthrough.html',results},null,2));
}
if(results.some(r=>r.failure))process.exitCode=1;
