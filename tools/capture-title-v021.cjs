// Record actual official-emulator frames; do not synthesize title animation.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),O=path.join(R,'reports/title-capture-v021');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{fs.mkdirSync(O,{recursive:true});const rows=[],begin=performance.now();
 for(let i=0;i<60;i++){
  const wait=begin+i*1000/15-performance.now();if(wait>0)await sleep(wait);
  const at=performance.now(),response=await fetch('http://127.0.0.1:43141/screen');
  if(!response.ok)throw Error(await response.text());
  const data=Buffer.from(await response.arrayBuffer()),file=String(i).padStart(3,'0')+'.png';
  fs.writeFileSync(path.join(O,file),data);rows.push({file,atMs:at-begin,sha256:crypto.createHash('sha256').update(data).digest('hex')});
 }
 const report={kind:'official-Vela-emulator-screen-recording',version:'0.2.1',audioIncluded:false,frames:rows.length,elapsedMs:performance.now()-begin,targetCaptureFPS:15,rows};
 fs.writeFileSync(path.join(O,'capture.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({frames:rows.length,elapsedMs:report.elapsedMs,unique:new Set(rows.map(x=>x.sha256)).size}));
})().catch(e=>{console.error(e);process.exitCode=1;});
