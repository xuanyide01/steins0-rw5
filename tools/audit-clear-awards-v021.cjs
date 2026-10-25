// Execute only original CLRFLG bookkeeping before its menu/achievement work.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{VM,ir}=require('./desktop-vm.cjs');const R=path.resolve(__dirname,'..'),clr=Object.values(ir.scripts).find(x=>x.name==='CLRFLG'),rows=[];
for(let ending=0;ending<6;ending++){
 const v=new VM(),t=v.s.threads[0];t.script=clr.id;t.pc=clr.labels[7+ending];let stopped=false;
 for(let guard=0;guard<1000;guard++){if(t.script===clr.id&&t.pc===60){stopped=true;break;}v.step(t);}assert.ok(stopped);
 const awards=Array.from({length:6},(_,i)=>i).filter(i=>v.get(t,'F',801+i));rows.push({ending,sourceEntryLabel:7+ending,awards,flags:awards.map(x=>801+x)});
}
assert.deepEqual(rows.map(x=>x.awards),[[0],[1],[2],[3],[4],[3,5]]);
const report={result:'passed',source:'Original Steam SC3 CLRFLG',scriptId:clr.id,bookkeepingOps:{baseFlagSetAtPC:57,extraFlagSetAtPC:59},endingTable:clr.memory[78],rows,notes:'Ending 5 sets F806 and additional F804; record both ending IDs 5 and 3. Not a chapter-title heuristic.'};fs.writeFileSync(path.join(R,'reports/clear-awards-v021-source.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
