const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v015'),base='http://127.0.0.1:43141/',log=path.resolve(R,'../steins0-environment/emulator.log');fs.mkdirSync(O,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)),logs=()=>fs.readFileSync(log,'utf8');
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at,ms=20000){const end=Date.now()+ms;while(Date.now()<end){if(re.test(logs().slice(at)))return;await sleep(50);}throw Error('Timeout '+re+'\n'+logs().slice(at).slice(-1200));}
async function click(x,y,re,delay=140){const at=logs().length;await req('click?x='+x+'&y='+y);if(re)await wait(re,at);await sleep(delay);}
async function shot(n,delay=600){await sleep(delay);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
function state(){const m=[...logs().matchAll(/STEINS0_RW5 frame (n\d+) (\d+) /g)].at(-1);assert.ok(m);return {node:m[1],cursor:+m[2]};}
async function menu(){await click(150,479,/STEINS0_RW5 mode menu/);}
async function configureMode(mode){await click(110,427,/STEINS0_RW5 mode config/);for(let i=0;i<3;i++){const at=logs().length;await click(70,147,/STORAGE_SET/);if(logs().slice(at).includes('"textMode":"'+mode+'"'))break;}await click(70,403,/STEINS0_RW5 mode title/);}
(async()=>{
 const boot=logs().lastIndexOf('NuttShell (NSH)');await wait(/Page show page_info:name:pages\/index/,boot,60000);const begin=logs().lastIndexOf('STEINS0_RW5 app created');await shot('01-title');
 await configureMode('character');await click(110,292,/STEINS0_RW5 frame n0 0 /);await click(216,230,/STEINS0_RW5 mode play/,0);
 for(let i=0;i<6;i++)await shot('02-typing-'+i,50);await shot('03-typing-completed',1000);
 // Enable AUTO in the menu, return to story, observe further original frames.
 await menu();await click(70,235,/STEINS0_RW5 mode menu/);const at=logs().length;await click(70,425,/STEINS0_RW5 mode play/);const initial=state();
 await wait(/STEINS0_RW5 frame n0 [1-9]\d* /,at,15000);await shot('04-auto-character-playback',800);
 await menu();const paused=state();await sleep(3000);assert.deepEqual(state(),paused);await shot('05-auto-paused-by-menu');
 await click(70,468,/STEINS0_RW5 mode title/);await configureMode('sentence');await click(110,292,/STEINS0_RW5 frame n0 0 /);await click(216,230,/STEINS0_RW5 mode play/);await shot('06-sentence-mode');await menu();await click(70,468,/STEINS0_RW5 mode title/);
 await configureMode('instant');await click(110,337,/STEINS0_RW5 list slots 0/);await click(70,173,/STEINS0_RW5 frame n0 1 /);await shot('07-legacy-save-instant');await menu();await click(70,468,/STEINS0_RW5 mode title/);
 const text=logs().slice(begin);assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|Assertion failed|PANIC!!!/.test(text));const rpk=path.join(R,'dist/com.codex.steins0.rw5.debug.0.1.5.rpk');
 const report={result:'passed-awaiting-typing-screenshot-review',sha256:crypto.createHash('sha256').update(fs.readFileSync(rpk)).digest('hex'),typingCaptures:6,autoAdvancedFrom:initial,menuPausesAuto:true,sentenceAndInstantModesOpened:true,legacySaveLoaded:{node:'n0',cursor:1},physicalDeviceTested:false};fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
