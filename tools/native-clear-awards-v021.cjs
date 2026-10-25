const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v021'),log=path.resolve(R,'../steins0-environment/emulator.log'),base='http://127.0.0.1:43141/',sleep=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync(O,{recursive:true});
const offset=()=>fs.statSync(log).size;
function since(at){const f=fs.openSync(log,'r'),n=fs.fstatSync(f).size,b=Buffer.alloc(Math.max(0,n-at));if(b.length)fs.readSync(f,b,0,b.length,at);fs.closeSync(f);return b.toString();}
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at){const end=Date.now()+60000;while(!re.test(since(at))){if(Date.now()>end)throw Error('Timeout '+re+'\n'+since(at).slice(-1600));await sleep(50);}}
async function click(x,y,re){const at=offset();await req('click?x='+x+'&y='+y);if(re)await wait(re,at);await sleep(150);return at;}
async function shot(n){await sleep(700);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
(async()=>{
 const begin=offset();await req('start');await wait(/startup animation ready/,begin);await shot('01-title');
 await click(110,382,/mode extra/);await click(70,191,/list routes 0/);
 for(let p=1;p<=3;p++)await click(350,486,new RegExp('list routes '+p));
 await shot('02-true-chapter-selection');await click(70,250,/list chapters 0/);await click(70,173,/frame n20 4561 /);await shot('03-original-true-chapter-card');
 await click(216,230,/mode play/);await click(150,479,/mode menu/);
 const endAt=await click(70,204,/mode end/);await wait(/STORAGE_SET/,endAt);await shot('04-true-ending-settlement');
 const stored=since(endAt);assert.ok(/"3":true/.test(stored)&&/"5":true/.test(stored),'Both original awards must be persisted');
 await click(70,148,/mode title/);await click(110,382,/mode extra/);await click(70,297,/list endings 0/);await shot('05-clear-list-va');
 await click(350,486,/list endings 1/);await shot('06-clear-list-true');await click(216,486,/mode extra/);await click(70,350,/mode title/);
 await click(110,337,/slots ready 0/);await click(70,173,/frame n0 1 /);await shot('07-legacy-save');await click(150,479,/mode menu/);await click(70,468,/mode title/);
 const text=since(begin);assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|PANIC!!!|Assertion failed/.test(text));
 const report={result:'passed-awaiting-visual-review',sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(R,'dist/com.codex.steins0.rw5.debug.0.2.1.rpk'))).digest('hex'),coldStart:true,trueChapterSkippedToSettlement:true,bothOriginalAwardsPersisted:true,bothClearListPagesOpened:true,legacyN0Cursor1Loaded:true,physicalDeviceTested:false};
 fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
