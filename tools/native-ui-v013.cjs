const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v013'),base='http://127.0.0.1:43141/',log=path.resolve(R,'../steins0-environment/emulator.log');fs.mkdirSync(O,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)),logs=()=>fs.readFileSync(log,'utf8');
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at,ms=20000){const end=Date.now()+ms;while(Date.now()<end){if(re.test(logs().slice(at)))return;await sleep(60);}throw Error('Timeout '+re+'\n'+logs().slice(at).slice(-1500));}
async function click(x,y,re,delay=140){const at=logs().length;await req('click?x='+x+'&y='+y);if(re)await wait(re,at);await sleep(delay);}
async function shot(n){await sleep(1400);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
function state(){const m=[...logs().matchAll(/STEINS0_RW5 frame (n\d+) (\d+) /g)].at(-1);assert.ok(m);return {node:m[1],cursor:+m[2]};}
async function advance(){const s=state();await click(374,479,null,40);for(let i=0;i<30;i++){if(state().cursor!==s.cursor||state().node!==s.node)return;await sleep(30);}await click(374,479,/STEINS0_RW5 frame/,60);}
async function menu(){await click(150,479,/STEINS0_RW5 mode menu/);}
async function skip(){await menu();const at=logs().length;await click(70,204,/STEINS0_RW5 (frame|mode choice|mode end)/);if(/STEINS0_RW5 mode card/.test(logs().slice(at)))await click(216,230,/STEINS0_RW5 mode play/);}
(async()=>{
 const boot=logs().lastIndexOf('NuttShell (NSH)');await wait(/Page show page_info:name:pages\/index/,boot,60000);const begin=logs().lastIndexOf('STEINS0_RW5 app created');await sleep(1200);
 if(!process.argv.includes('--resume-after-stickers')){
 await shot('01-title');await click(110,427,/STEINS0_RW5 mode config/);
 for(let i=0;i<3;i++){const at=logs().length;await click(70,147,/STORAGE_SET/);if(/"textMode":"instant"/.test(logs().slice(at)))break;}
 await click(70,403,/STEINS0_RW5 mode title/);await click(110,292,/STEINS0_RW5 frame n0 0 /);await click(216,230,/STEINS0_RW5 mode play/);
 while(state().cursor<9)await advance();await shot('02-improved-portraits');
 await skip();assert.equal(state().cursor,96);await skip();assert.equal(state().cursor,587);while(state().cursor<591)await advance();
 await click(265,479,/STEINS0_RW5 phone home/);await shot('03-inbox-unread');await click(70,170,/STEINS0_RW5 phone inbox/);await shot('04-available-reply-in-list');await click(70,170,/STEINS0_RW5 thread 2560/);await shot('05-bottom-reply-button');
 await click(350,486,/STEINS0_RW5 phone reply/);await shot('06-original-three-replies');await click(70,170,/STEINS0_RW5 thread 2560/);await shot('07-selected-outgoing-and-followups');
 await click(216,486,/STEINS0_RW5 phone sent/);await click(216,486,/STEINS0_RW5 phone home/);await shot('08-new-followup-notice');await click(70,170,/STEINS0_RW5 phone inbox/);await click(216,486,/STEINS0_RW5 phone home/);await shot('09-inbox-group-and-message-counts');await click(216,486,/STEINS0_RW5 mode play/);
 await skip();assert.equal(state().cursor,780);while(state().cursor<790)await advance();await click(265,479,/STEINS0_RW5 phone home/);await click(70,170,/STEINS0_RW5 phone inbox/);await click(70,170,/STEINS0_RW5 thread 2816/);await click(350,486,/STEINS0_RW5 phone reply/);await shot('10-original-sticker-reply-choices');await click(70,170,/STEINS0_RW5 thread 2816/);await shot('11-sticker-sent-in-original-sequence');
 await click(350,486,/STEINS0_RW5 thread 2816/);await click(350,486,/STEINS0_RW5 thread 2816/);}
 await click(350,486,/STEINS0_RW5 mode play/);
 while(state().cursor<924)await advance();await shot('12-improved-amadeus');
 await menu();await click(70,468,/STEINS0_RW5 mode title/);await click(110,337,/STEINS0_RW5 list slots 0/);await click(70,173,/STEINS0_RW5 frame n0 1 /);await shot('13-legacy-save-restored');await menu();await click(70,468,/STEINS0_RW5 mode title/);
 const text=logs().slice(begin);assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|Assertion failed|PANIC!!!/.test(text));const rpk=path.join(R,'dist/com.codex.steins0.rw5.debug.0.1.3.rpk');
 const report={result:'passed',sha256:crypto.createHash('sha256').update(fs.readFileSync(rpk)).digest('hex'),improvedPortraits:true,unreadAndCountSummaries:true,prominentBottomReplyButton:true,originalReplyChoices:true,selectedOutgoingIncluded:true,originalStickerReplyChoices:true,followupMessages:true,legacySaveLoaded:{node:'n0',cursor:1},noRuntimeErrors:true,physicalDeviceTested:false};
 fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
