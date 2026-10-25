const fs=require('fs'),path=require('path'),assert=require('assert/strict');const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v016'),log=path.resolve(R,'../steins0-environment/emulator.log'),base='http://127.0.0.1:43141/',sleep=ms=>new Promise(r=>setTimeout(r,ms));
function since(at){const f=fs.openSync(log,'r'),size=fs.fstatSync(f).size,b=Buffer.alloc(size-at);fs.readSync(f,b,0,b.length,at);fs.closeSync(f);return b.toString();}
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function click(x,y,re){const at=fs.statSync(log).size;await req('click?x='+x+'&y='+y);if(re){const end=Date.now()+15000;while(!re.test(since(at))){if(Date.now()>end)throw Error('Timeout '+re+'\n'+since(at).slice(-1000));await sleep(20);}}await sleep(35);}
async function shot(n){await sleep(1500);fs.writeFileSync(path.join(O,n+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
(async()=>{
 await click(110,382,/mode extra/);await click(70,201,/list routes/);await click(350,486,/list routes 1/);await click(70,173,/list chapters/);await click(70,249,/frame n25 519 /);await click(216,230,/mode play/);
 for(let cursor=520;cursor<=720;cursor++)await click(374,479,new RegExp('frame n25 '+cursor+' '));
 await click(265,479,/phone home/);await click(70,170,/phone inbox/);await click(70,170,/thread 5376/);await click(350,486,/phone reply/);await shot('12-longest-reply-options');await click(70,326,/thread 5376 0 40/);await shot('13-forty-messages-one-page');
 for(let i=0;i<20;i++)await req('drag?x0=220&y0=420&x1=220&y1=170');await shot('14-forty-messages-scroll-bottom');await click(350,486,/mode play/);await shot('15-return-after-long-chat');await click(150,479,/mode menu/);await click(70,468,/mode title/);
 const p=path.join(O,'report.json'),r=JSON.parse(fs.readFileSync(p));r.longestOriginalReplyOpenedNatively={node:'n25',cursor:720,replyIndex:2,messages:40};r.longChatScrolledAndReturned=true;fs.writeFileSync(p,JSON.stringify(r,null,2));console.log('Original 40-message conversation opened, scrolled and returned successfully');
})().catch(e=>{console.error(e);process.exitCode=1;});
