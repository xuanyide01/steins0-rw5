const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto'),cp=require('child_process'),{promisify}=require('util');
const run=promisify(cp.execFile),R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v017'),log=path.resolve(R,'../steins0-environment/emulator.log'),base='http://127.0.0.1:43141/',adb=path.resolve(R,'../starry-rw5/node_modules/@miwt/adb/bin/win/adb.exe'),sleep=ms=>new Promise(r=>setTimeout(r,ms));fs.mkdirSync(O,{recursive:true});
function offset(){return fs.statSync(log).size;}
function since(at){const f=fs.openSync(log,'r'),n=fs.fstatSync(f).size,b=Buffer.alloc(Math.max(0,n-at));if(b.length)fs.readSync(f,b,0,b.length,at);fs.closeSync(f);return b.toString();}
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at,ms=25000){const end=Date.now()+ms;while(Date.now()<end){if(re.test(since(at)))return;await sleep(35);}throw Error('Timeout '+re+'\n'+since(at).slice(-1800));}
async function click(x,y,re,delay=120){const at=offset(),t=Date.now();await req('click?x='+x+'&y='+y);if(re)await wait(re,at);await sleep(delay);return {at,elapsedMs:Date.now()-t};}
async function shot(n){await sleep(1500);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
async function memory(){const {stdout}=await run(adb,['-s','emulator-5556','shell','free'],{windowsHide:true,timeout:20000});const m=stdout.match(/^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+Umem/m);assert.ok(m);return {usedBytes:+m[2],freeBytes:+m[3],maxUsedBytes:+m[4]};}
async function menu(){await click(150,479,/mode menu/);}
async function lastPage(){for(let p=1;p<=7;p++)await click(350,486,new RegExp('slots ready '+p));}
(async()=>{
 const begin=offset(),coldStarts=[];
 // Each run starts from a separately cold-booted SDK: this SDK's debugger can
 // assert in uv_loop_init if am stop/start is repeated within one OS boot.
 for(let i=0;i<1;i++){
  const at=offset(),time=Date.now();await req('start');await wait(/startup animation ready/,at,60000);const text=since(at);assert.ok(!text.includes('graph lazy load'));assert.ok(text.indexOf('startup music ready')<text.indexOf('startup animation ready'));
  coldStarts.push({instance:i+1,controllerRoundTripToWarmupMs:Date.now()-time,memory:await memory(),noEagerGraphRead:true});
 }
 await shot('01-staged-title-startup');await click(110,427,/mode config/);for(let i=0;i<3;i++){const r=await click(70,147,/STORAGE_SET/);if(since(r.at).includes('"textMode":"instant"'))break;}await click(70,403,/mode title/);
 const startAt=offset();await click(110,292,/frame n0 0 /);assert.ok(since(startAt).includes('graph lazy load'));await click(216,230,/mode play/);for(let i=0;i<9;i++)await click(374,479,/STEINS0_RW5 frame/);await shot('02-first-game-scene');
 await menu();const firstPage=await click(70,116,/slots ready 0/);await shot('03-slot-summaries');await lastPage();const storySave=await click(70,173,/mode overwrite|saved 28/);if(since(storySave.at).includes('mode overwrite'))await click(70,140,/saved 28/);await wait(/mode play/,storySave.at);await shot('04-save-directly-returned-to-story');
 await menu();const warmPages=[];for(let i=0;i<3;i++){const r=await click(70,116,/slots ready 0/);warmPages.push(r.elapsedMs);await click(216,486,/mode menu/);}await click(70,468,/mode title/);
 await click(110,382,/mode extra/);await click(70,201,/list routes 0/);await click(70,404,/list chapters 0/);await click(350,486,/list chapters 1/);await click(70,404,/frame n17 1870 /);await click(216,230,/mode play/);await menu();await click(70,204,/mode choice/);await shot('05-amadeus-critical-call');
 await click(70,307,/mode menu/);await click(70,116,/slots ready 0/);await lastPage();const saveAt=await click(70,250,/mode overwrite|saved 29/);if(since(saveAt.at).includes('mode overwrite'))await click(70,140,/saved 29/);await shot('06-save-directly-returned-to-phone-choice');
 await click(70,307,/mode menu/);await click(70,160,/slots ready 0/);await lastPage();await click(70,250,/mode choice/);await shot('07-load-restores-critical-call');
 await click(70,307,/mode menu/);await click(70,116,/slots ready 0/);await lastPage();await click(70,250,/mode overwrite/);await click(70,140,/saved 29/);await shot('08-overwrite-returned-to-phone-choice');
 await click(70,254,/phone home/);await click(70,415,/phone calls/);await shot('09-amadeus-phone-operation-label');await click(216,486,/phone home/);await click(216,486,/mode choice/);await click(70,307,/mode menu/);await click(70,468,/mode title/);
 const text=since(begin);assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|Assertion failed|PANIC!!!|out of memory/i.test(text));
 const file=path.join(R,'dist/com.codex.steins0.rw5.debug.0.1.7.rpk'),report={result:'passed-awaiting-visual-review',sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),coldStarts,physicalDeviceTested:false,startupImprovementIsStagingNotMeasuredPhysicalPeakRAM:true,firstSlotPageControllerLatencyMs:firstPage.elapsedMs,warmSlotPageControllerLatenciesMs:warmPages,latenciesIncludeInputTransportAndNotDeviceBenchmark:true,saveReturnsToStory:true,saveAndOverwriteReturnToCriticalCall:true,criticalCallLoaded:true,amadeusCallLabelOpened:true};fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
