const {VM,ir}=require('./desktop-vm.cjs'),fs=require('fs');
const v=new VM();let count=0;const output=[];
for(let i=0;i<3000;i++){
 const f=v.next({tickLimit:10000});if(f.type==='text')count++;
 if(f.type==='text'&&f.site.startsWith('SG0_00_04:')&&Number(f.site.split(':')[1])>=140){
  const t=v.s.threads[0];output.push({site:f.site,words:Object.fromEntries([39,6600,6602,6640,6641,6642,5229,5232,5227].map(i=>[i,v.get(t,'W',i)])),speaker:Array.from(f.speaker,x=>x.charCodeAt(0).toString(16))});if(output.length===12)break;
 }
 if(f.type==='choice')v.answer(f,false);
}
const script=Object.values(ir.scripts).find(x=>x.name==='macrosys2');console.log(JSON.stringify({output,resetOps:script.ops.map((o,i)=>o[0]==='SG0Phone28'?{pc:i,label:script.siteLabels[i]}:null).filter(Boolean),label612:script.labels['612'],label613:script.labels['613']},null,2));
