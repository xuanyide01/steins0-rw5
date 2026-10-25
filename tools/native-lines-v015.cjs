const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v015'),base='http://127.0.0.1:43141/',log=path.resolve(R,'../steins0-environment/emulator.log'),sleep=ms=>new Promise(r=>setTimeout(r,ms)),logs=()=>fs.readFileSync(log,'utf8');
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function click(x,y,re,delay=100){const at=logs().length;await req('click?x='+x+'&y='+y);if(re){const end=Date.now()+15000;while(!re.test(logs().slice(at))){if(Date.now()>end)throw Error('Timeout '+re);await sleep(30);}}await sleep(delay);return at;}
async function shot(n,delay){await sleep(delay);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
(async()=>{
 await click(110,427,/mode config/);for(let i=0;i<3;i++){const at=await click(70,147,/STORAGE_SET/);if(logs().slice(at).includes('"textMode":"character"'))break;}await click(70,403,/mode title/);
 await click(110,292,/frame n0 0 /);await click(216,230,/mode play/);await click(150,479,/mode menu/);const at=await click(70,204,/frame n0 96 /,0);if(logs().slice(at).includes('mode card'))await click(216,230,/mode play/,0);
 for(let i=0;i<4;i++)await shot('08-multiline-'+i,100);await shot('09-multiline-complete',1400);await click(150,479,/mode menu/);await click(70,468,/mode title/);
 const report=JSON.parse(fs.readFileSync(path.join(O,'report.json')));report.multilineNativeCapturesAt={node:'n0',cursor:96};fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log('Multiline captures complete; visual review required');
})().catch(e=>{console.error(e);process.exitCode=1;});
