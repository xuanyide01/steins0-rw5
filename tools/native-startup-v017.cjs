const fs=require('fs'),path=require('path'),assert=require('assert/strict');const R=path.resolve(__dirname,'..'),O=path.join(R,'native-test-results-v017'),log=path.resolve(R,'../steins0-environment/emulator.log'),base='http://127.0.0.1:43141/',sleep=ms=>new Promise(r=>setTimeout(r,ms));
function offset(){return fs.statSync(log).size;}function since(at){const f=fs.openSync(log,'r'),n=fs.fstatSync(f).size,b=Buffer.alloc(n-at);fs.readSync(f,b,0,b.length,at);fs.closeSync(f);return b.toString();}
async function req(p){const r=await fetch(base+p);if(!r.ok)throw Error(await r.text());return r;}
async function wait(re,at){const end=Date.now()+60000;while(!re.test(since(at))){if(Date.now()>end)throw Error('Timeout '+re+'\n'+since(at).slice(-1600));await sleep(35);}}
async function click(x,y,re){const at=offset();await req('click?x='+x+'&y='+y);await wait(re,at);await sleep(150);}
async function shot(name){await sleep(1500);fs.writeFileSync(path.join(O,name+'.png'),Buffer.from(await(await req('screen')).arrayBuffer()));}
(async()=>{
 const file=path.join(O,'report.json'),r=JSON.parse(fs.readFileSync(file));
 if(process.argv.includes('--legacy')){
  await click(110,337,/slots ready 0/);await click(70,173,/frame n0 1 /);await shot('10-original-legacy-save-loaded');await click(150,479,/mode menu/);await click(70,468,/mode title/);r.legacySaveLoadedNatively={node:'n0',cursor:1};
 }else{
  const at=offset();await req('start');await wait(/startup animation ready/,at);const text=since(at);assert.ok(!text.includes('graph lazy load'));assert.ok(!/STEINS0_RW5 error|ReferenceError|TypeError|PANIC!!!|Assertion failed/.test(text));
  r.independentSystemColdBoots=(r.independentSystemColdBoots||1)+1;r.coldTitleNoGraphRead=true;
  if(process.argv.includes('--start')){await click(110,292,/frame n0 0 /);await click(216,230,/mode play/);await shot('11-cold-boot-start-game');await click(150,479,/mode menu/);await click(70,468,/mode title/);r.gameStartAfterColdBoot=true;}
 }
 fs.writeFileSync(file,JSON.stringify(r,null,2));console.log('Supplementary native check passed '+process.argv.slice(2).join(' '));
})().catch(e=>{console.error(e);process.exitCode=1;});
