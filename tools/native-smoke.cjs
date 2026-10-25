const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results'),base='http://127.0.0.1:43141/',log=path.resolve(R,'../steins0-environment/emulator.log');fs.mkdirSync(O,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)),logs=()=>fs.readFileSync(log,'utf8');
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at,ms=15000){const end=Date.now()+ms;while(Date.now()<end){if(re.test(logs().slice(at)))return;await sleep(45);}throw Error('Timeout '+re+'\n'+logs().slice(at).slice(-700));}
async function click(x,y,re){const at=logs().length,t=Date.now();await req('click?x='+x+'&y='+y);if(re)await wait(re,at);await sleep(150);return Date.now()-t;}
async function shot(n){await sleep(200);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
function state(){const m=[...logs().matchAll(/STEINS0_RW5 frame (n\d+) (\d+) /g)].at(-1);assert.ok(m);return {node:m[1],cursor:+m[2]};}
async function advance(){const s=state(),re=new RegExp('STEINS0_RW5 frame '+s.node+' '+(s.cursor+1)+' ');const at=logs().length;await click(375,478);if(!re.test(logs().slice(at)))await click(375,478,re);}
async function saveAt(x,y,key){let at=logs().length;await click(x,y,/STEINS0_RW5 mode overwrite|STORAGE_SET/);if(/STEINS0_RW5 mode overwrite/.test(logs().slice(at)))await click(70,145,new RegExp('STORAGE_SET.*'+key));else assert.ok(logs().slice(at).includes(key));}
async function menu(){await click(150,478,/STEINS0_RW5 mode menu/);}
async function resume(){await click(70,463,/STEINS0_RW5 mode play/);}
async function skip(){await menu();return click(170,250,/STEINS0_RW5 (frame|mode choice|mode end)/);}
async function title(){await menu();await req('drag?x0=245&y0=430&x1=245&y1=240');await click(70,460,/STEINS0_RW5 mode title/);}
(async()=>{
 const boot=logs().lastIndexOf('NuttShell (NSH)'),begin=logs().lastIndexOf('STEINS0_RW5 app created');await wait(/Page show page_info:name:pages\/index/,boot,45000);await sleep(1000);if(process.argv.includes('--resume'))await title();await shot('title-full-composite');
 const blankAt=logs().length;await click(380,310);assert.ok(!/STEINS0_RW5 frame/.test(logs().slice(blankAt)));
 const startMs=await click(100,310,/STEINS0_RW5 frame n0 0 /);await shot('chapter-title');await click(216,250,/STEINS0_RW5 mode play/);await shot('first-text');await click(210,350);if(state().cursor===0)await click(210,350,/STEINS0_RW5 frame n0 1 /);await click(375,478);await shot('white-transition');
 await menu();await click(70,145,/STEINS0_RW5 list slots 0/);await shot('save-01-04');await saveAt(180,150,'steins0_rw5_slot_v2_1');await click(70,145,/STEINS0_RW5 list slots 0/);for(let i=0;i<7;i++)await click(355,478);await shot('save-29-30');await saveAt(180,231,'steins0_rw5_slot_v2_30');await resume();
 while(state().cursor<12)await advance();await click(375,478);await shot('original-sprites');
 const rows=JSON.parse(fs.readFileSync(path.join(R,'src/common/story/0/0.txt'))).frames,long=rows.findIndex((r,i)=>i>12&&r[1].length>65);if(long>12){while(state().cursor<long)await advance();await click(375,478);await shot('long-text');const at=logs().length;await req('drag?x0=250&y0=430&x1=250&y1=320');assert.ok(!/STEINS0_RW5 frame/.test(logs().slice(at)));await shot('long-text-scrolled');}
 await menu();await click(70,303);await click(70,357);await resume();const before=state();await sleep(5500);const after=state();assert.ok(after.cursor>before.cursor,'AUTO did not advance');await shot('autoplay');await click(60,478);await menu();await click(70,145,/STEINS0_RW5 list slots 0/);await click(216,478,/STEINS0_RW5 mode menu/);await resume();
 // Reach an actual RINE window: SG0_00_03 begins at587, first reply at591.
 const skips=[];while(state().node==='n0'&&state().cursor<587)skips.push(await skip());assert.equal(state().cursor,587);for(let i=0;i<4;i++)await advance();await click(265,478,/STEINS0_RW5 mode menu/);await shot('phone-home');await click(70,145,/STEINS0_RW5 list messages/);await shot('rine-inbox');await click(70,150,/STEINS0_RW5 mode phone/);await shot('rine-body');await click(75,478,/STEINS0_RW5 mode choice/);await shot('rine-replies');await click(70,145,/STEINS0_RW5 mode phone/);await shot('rine-sent-conversation');await click(345,478,/STEINS0_RW5 mode play/);
 // Skip must halt at the power-off decision after the ordinary calls.
 let stopped=false;for(let i=0;i<30;i++){const at=logs().length;skips.push(await skip());if(/STEINS0_RW5 mode card/.test(logs().slice(at)))await click(216,250,/STEINS0_RW5 mode play/);if(/STEINS0_RW5 mode choice/.test(logs().slice(at))){stopped=true;break;}}
 assert.ok(stopped);await shot('critical-phone-decision');await click(70,198,/STEINS0_RW5 (frame|mode choice)/);await shot('critical-deferred');
 const text=logs().slice(begin);assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|Assertion failed|PANIC!!!/.test(text));
 const report={result:'passed',sha256:require('crypto').createHash('sha256').update(fs.readFileSync(path.join(R,'dist/com.codex.steins0.rw5.debug.0.1.0.rpk'))).digest('hex'),startMilliseconds:startMs,skipMilliseconds:skips,longTextScrolled:long>12,thirtySlotsUI:true,dialogueTapAdvances:true,dragDoesNotAdvance:true,autoplayAdvances:true,originalRineReplyAndSentConversation:true,skipStopsAtCriticalPhone:true,physicalDeviceTested:false};fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1});
