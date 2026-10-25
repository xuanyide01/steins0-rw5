const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v016'),base='http://127.0.0.1:43141/',log=path.resolve(R,'../steins0-environment/emulator.log');fs.mkdirSync(O,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));function logs(){const f=fs.openSync(log,'r'),n=fs.fstatSync(f).size,b=Buffer.alloc(Math.min(n,1500000));fs.readSync(f,b,0,b.length,n-b.length);fs.closeSync(f);return b.toString();}
function since(at){const f=fs.openSync(log,'r'),n=fs.fstatSync(f).size,b=Buffer.alloc(Math.max(0,n-at));if(b.length)fs.readSync(f,b,0,b.length,at);fs.closeSync(f);return b.toString();}
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at,ms=20000){const end=Date.now()+ms;while(Date.now()<end){if(re.test(since(at)))return;await sleep(50);}throw Error('Timeout '+re+'\n'+since(at).slice(-1300));}
async function click(x,y,re,delay=100){const at=fs.statSync(log).size;await req('click?x='+x+'&y='+y);if(re)await wait(re,at);await sleep(delay);return at;}
async function shot(n){await sleep(1100);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
function state(){const m=[...logs().matchAll(/STEINS0_RW5 frame (n\d+) (\d+) /g)].at(-1);assert.ok(m);return {node:m[1],cursor:+m[2]};}
async function menu(){await click(150,479,/mode menu/);}
(async()=>{
 const boot=Math.max(0,fs.statSync(log).size-1500000);await wait(/Page show page_info:name:pages\/index/,boot,60000);await sleep(900);const begin=fs.statSync(log).size;
 await shot('01-title-safe-footer');await click(110,427,/mode config/);for(let i=0;i<3;i++){const at=await click(70,147,/STORAGE_SET/);if(since(at).includes('"textMode":"instant"'))break;}await click(70,403,/mode title/);
 await click(110,292,/frame n0 0 /);await click(216,230,/mode play/);for(let i=0;i<9;i++)await click(374,479,/STEINS0_RW5 frame/);await shot('02-shared-daru-expression');for(let i=0;i<3;i++)await click(374,479,/STEINS0_RW5 frame/);await shot('03-two-actor-expressions');
 await menu();await click(70,204,/frame n0 934 /);await shot('04-next-real-chapter-card');await click(216,230,/mode play/);await menu();await click(70,204,/mode choice/);await shot('05-skip-stops-important-phone');await click(70,307,/mode menu/);await click(70,468,/mode title/);
 await click(110,382,/mode extra/);await click(70,201,/list routes/);await click(70,173,/list chapters/);await click(70,326,/frame n0 587 /);await click(216,230,/mode play/);for(let i=0;i<4;i++)await click(374,479,/STEINS0_RW5 frame/);
 await click(265,479,/phone home/);await click(70,170,/phone inbox/);await click(70,170,/thread 2560/);await click(350,486,/phone reply/);await click(70,170,/thread-read 2560 0/);await shot('06-single-page-conversation-top');
 for(let i=0;i<4;i++)await req('drag?x0=220&y0=420&x1=220&y1=170');await shot('07-single-page-conversation-bottom');await click(350,486,/mode play/);await shot('08-return-no-false-unread');await menu();await click(70,468,/mode title/);
 await click(110,382,/mode extra/);await click(70,147,/gallery/);await shot('09-gallery-shared-hq-cg');await click(75,180,/STEINS0_RW5 cg/);await shot('10-higher-quality-cg');await click(216,482,/gallery/);await click(216,482,/mode extra/);await click(70,279,/mode title/);
 await click(110,337,/list slots 0/);await click(70,173,/frame n0 1 /);await shot('11-legacy-save-restored');await menu();await click(70,468,/mode title/);
 const text=since(begin);assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|Assertion failed|PANIC!!!/.test(text));const rpk=path.join(R,'dist/com.codex.steins0.rw5.debug.0.1.6.rpk');const report={result:'passed-awaiting-visual-review',sha256:crypto.createHash('sha256').update(fs.readFileSync(rpk)).digest('hex'),nextChapterAt:{node:'n0',cursor:934},importantPhoneStop:true,sharedBodyAndExpressionsOpened:true,singlePageConversationScrolled:true,replyReadStateRetained:true,originalCGGalleryOpened:true,legacySaveLoaded:{node:'n0',cursor:1},physicalDeviceTested:false};fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
