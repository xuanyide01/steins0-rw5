/* Desktop-only SC3 reference executor. Never copy this file or the IR into src.
 * Original calculations and cooperative presentation threads run at conversion
 * time; the watch will receive bounded scene blocks and explicit choice edges.
 * Unknown reachable instructions fail closed, with the original source site.
 */
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const ir=JSON.parse(fs.readFileSync(path.resolve(root,'../steins0-probe/vm-code.json'),'utf8'));
for(const script of Object.values(ir.scripts)){script.siteLabels=[];let label;const at={};for(const [l,p] of Object.entries(script.labels))at[p]=l;for(let i=0;i<script.ops.length;i++){if(at[i]!==undefined)label=at[i];script.siteLabels[i]=label;}}
const copy=x=>JSON.parse(JSON.stringify(x));
const presentation=new Set(`BGsetLink BGsetLink2 SetBgCutin SetBgCutin2 CharaLayerLoad
 MessWindowCloseEx MessWindowClosedWait MessWindowFastClose MessWindowOpen
 MessWindowOpenEx MessWindowOpenedWait MesVoiceWait MesMain MesClsAll
 MesSetSavePointRL MesSSetSavePointRL MesSSetSavePoint MesSync_00 MesSync_01
 MesSync_02 MesSync_03 MesSync_04 MesSMain MesS2VMain SetRevMesScx
 AutoSave_FF AutoSaveSetSavePointRL AutoSaveMain AutoSave_01 Save_2E Save_2F Save_28 Save_29
 BGMplay BGMstop BGMflag SEplay SEplay2 SEplay3 SEplay_01 SEplay_02 SEplay2_01 SEplay2_02
 SEstop SEstop2 SEstop3 SSEplay VoiceStop VoiceStop2 VoiceStop3 VoicePlay2 VoicePlay3
 ResetSoundAll SetDic2 SetEVflag SetAchievement PadAct Presence PresenceEx SetPlayMode
 EffectWaveInit EffectWaveSet PackFileAddBind ScriptKeyWait_00 ScriptKeyWait_01
 EndMovie MovieMain MovieMain_00 MovieMain_01 MovieMain_02 MovieMain_03
 PlayMovieWait SG0KeyboardJump01 SG0Control70 SG0Control71`.split(/\s+/).filter(Boolean));
class VM {
 constructor(saved){
  this.s=saved?copy(saved):{vars:{},banks:copy(ir.banks),threads:[],clock:0,nextThread:1,phone:{messages:[],history:[],contact:0},events:[],root:16,frames:0};
  this.stats={instructions:0,opcodes:{},threads:{},waits:{},scripts:{}};this.trace=[];
  if(!saved)this.s.threads.push(this.thread(13,2,0));
 }
 thread(script,label,group){const x=ir.scripts[script];if(!x||x.labels[label]===undefined)throw Error('Invalid entry '+script+':'+label);return {id:this.s.nextThread++,script,pc:x.labels[label],group,stack:[],t:{},wake:0,dead:false};}
 get(t,g,n){return (g==='T'?t.t:this.s.vars)[g+':'+n]??0;}
 put(t,g,n,v){const bag=g==='T'?t.t:this.s.vars;if(g==='F')v=v?1:0;if(v===0)delete bag[g+':'+n];else bag[g+':'+n]=v;if(g==='F'&&n===2620&&!v){this.s.phone.generation=(this.s.phone.generation||0)+1;this.s.phone.ignored=[];}}
 val(e,t){
  if(!Array.isArray(e))return e;const op=e[0],a=this.val(e[1],t);
  if(['W','T','F'].includes(op))return this.get(t,op,a);
  if(op==='L')return [t.script,a];
  if(op==='R')return 0; // deterministic presentation-only random seed, audited below
  if(op==='MR'){const b=this.val(e[2],t);if(!Array.isArray(a))throw Error('Non-table pointer '+JSON.stringify(a));const row=ir.scripts[a[0]].memory[a[1]];if(!row||b<0||b>=row.length)throw Error('Table bounds '+a+':'+b);return row[b];}
  if(e.length===2){if(op==='-')return -a;if(op==='+')return +a;if(op==='!')return +!a;if(op==='~')return ~a;}
  const b=this.val(e[2],t);
  switch(op){case '+':return a+b;case '-':return a-b;case '*':return a*b;case '/':return b?Math.trunc(a/b):0;case '%':return b?a%b:0;case '&':return a&b;case '|':return a|b;case '^':return a^b;case '<<':return a<<b;case '>>':return a>>b;case '==':return +(JSON.stringify(a)===JSON.stringify(b));case '!=':return +(JSON.stringify(a)!==JSON.stringify(b));case '<':return +(a<b);case '<=':return +(a<=b);case '>':return +(a>b);case '>=':return +(a>=b);default:throw Error('Expression '+op);}
 }
 set(t,o){const target=o[1],n=this.val(target[1],t),v=this.val(o[3],t),a=this.get(t,target[0],n);let b=v;
  switch(o[2]){case '++':case '+=':b=a+v;break;case '--':case '-=':b=a-v;break;case '*=':b=a*v;break;case '/=':b=v?Math.trunc(a/v):0;break;case '%=':b=v?a%v:0;break;case '&=':b=a&v;break;case '|=':b=a|v;break;case '^=':b=a^v;break;case '<<=':b=a<<v;break;case '>>=':b=a>>v;break;}
  this.put(t,target[0],n,b);
 }
 jump(t,script,label,call=false){const x=ir.scripts[script];if(!x||x.labels[label]===undefined)throw Error('Jump target '+script+':'+label);if(call){if(t.stack.length>48)throw Error('Call depth');t.stack.push([t.script,t.pc+1]);}t.script=script;t.pc=x.labels[label];if(x.name.startsWith('SG0_')){this.s.root=script;this.put(t,'W',4343,script);this.put(t,'W',1,script);}}
 ret(t){if(!t.stack.length){t.dead=true;return;}const x=t.stack.pop();[t.script,t.pc]=x;}
 source(t){const x=ir.scripts[t.script];return {script:x.name,id:t.script,pc:t.pc,label:x.siteLabels[t.pc]};}
 swap(t,ma,mb,ch){const slot=m=>{for(let i=0;i<8;i++)if(m&(1<<i))return i;throw Error('Invalid buffer '+m);};const a=slot(ma),b=slot(mb),base=ch?5100:4500,f=ch?2410:2400;
  const v=this.get(t,'F',f+a);this.put(t,'F',f+a,this.get(t,'F',f+b));this.put(t,'F',f+b,v);for(let j=0;j<40;j++){const x=base+40*a+j,y=base+40*b+j,z=this.get(t,'W',x);this.put(t,'W',x,this.get(t,'W',y));this.put(t,'W',y,z);}}
 phone(t,o){
  const p=this.s.phone,v=i=>this.val(o[i],t),site=this.source(t);p.history.push({site,op:o[0],args:o.slice(1).map(x=>this.val(x,t))});if(p.history.length>64)p.history.shift();
  // Neutral recording adapter, not final native phone emulation. Route-visible
  // flags are only set by an explicit decision in the graph compiler.
  if(o[0]==='SG0Phone01'){p.messages=[];return;}
  if(['SG0Phone28','SG0Phone29','SG0Phone2F'].includes(o[0])){if(o[0]==='SG0Phone28')this.s.events.push({type:'rineReset',scope:site.script==='macrosys2'&&site.label==='612'?'display':'history',source:site.script+':'+site.label});if(o[0]==='SG0Phone29'){p.display=[];p.awaitingTable=true;p.relative=[];}return;}
  if(o[0]==='SG0Phone2A'){p.contact=v(1);return;}
  if(o[0]==='SG0Phone2B'||o[0]==='SG0Phone2C'){const row={contact:p.contact,id:v(1),outgoing:o[0]==='SG0Phone2C',script:t.script};if(p.awaitingTable)(p.relative??=[]).push(row);else{row.id+=this.get(t,'W',6655);p.messages.push(row);this.s.events.push({type:'message',...row});}return;}
  if(o[0]==='SG0Phone2E'){const row={contact:p.contact,sender:v(1),outgoing:v(1)===0,stamp:!!v(2),id:v(3),base:this.get(t,'W',6655),date:this.get(t,'W',1029),script:t.script};(p.display??=[]).push(row);this.s.events.push({type:'message',...row});return;}
  if(o[0]==='SG0Phone30'){p.replyTable=v(1);return;}
  if(o[0]==='SG0Phone2F')return;
  if(o[0]==='SG0Phone32'){p.textTable=[0,v(1)];this.put(t,'W',6655,v(1)*256);for(const row of p.relative||[]){row.id+=v(1)*256;p.messages.push(row);this.s.events.push({type:'message',...row});}p.relative=[];p.awaitingTable=false;return;}
  if(o[0]==='SG0Phone0B'){p.replyTable=null;return;}
  if(o[0]==='SG0Phone0A'){p.callback=[t.script,v(1)];this.s.events.push({type:'rineReply',callback:p.callback.slice(),base:this.get(t,'W',6655),contact:p.contact});return;}
  if(o[0]==='SG0Phone0C'){p.replyContact=v(1);p.replyStamp=!!v(2);p.replies=[];return;}
  if(o[0]==='SG0Phone0D'){(p.replies??=[]).push({id:v(1),script:t.script,label:v(2)});return;}
  if(o[0]==='SG0Phone0E')return;
  if(o[0]==='SG0Phone0F'){const row={contact:p.contact,sender:v(1),outgoing:v(1)===0,stamp:!!v(2),id:v(3)};p.messages.push(row);(p.display??=[]).push(row);return;}
  throw Error('Unverified native phone '+JSON.stringify(o));
 }
 step(t){
  if(t.dead||t.wake>this.s.clock)return null;const x=ir.scripts[t.script],o=x.ops[t.pc];if(!o)throw Error('Script overrun '+JSON.stringify(this.source(t)));
  const op=o[0],v=i=>this.val(o[i],t),g=(group,n)=>this.get(t,group,n),put=(group,n,b)=>this.put(t,group,n,b);this.stats.instructions++;this.stats.opcodes[op]=(this.stats.opcodes[op]||0)+1;this.stats.scripts[x.name]=true;
  this.trace.push({...this.source(t),op});if(this.trace.length>30)this.trace.shift();
  if(op==='text'){if(t.id!==1)throw Error('Dialogue in background thread '+x.name);for(const effect of o[5]||[])this.set(t,effect);t.pc++;this.s.frames++;return {type:'text',speaker:o[1],text:o[2],site:x.name+':'+o[3],script:t.script,pc:t.pc-1};}
  if(op==='set')this.set(t,o);
  else if(op==='Return'){this.ret(t);return null;}
  else if(op==='End'){t.dead=true;return null;}
  else if(op==='Jump'){this.jump(t,t.script,v(1));return null;}
  else if(op==='If'||op==='IfInv'){if(op==='If'?v(1):!v(1)){this.jump(t,t.script,v(2));return null;}}
  else if(op==='FlagOnJump'||op==='FlagOffJump'){
   if(this.decisions&&t.id===1&&x.name.startsWith('SG0_')&&op==='FlagOnJump'&&v(1)===2620&&!g('F',2620)){
    const mode=g('W',6602),key=t.script+':'+v(2)+':'+mode+':'+(this.s.phone.generation||0);if(!(this.s.phone.ignored||[]).includes(key))return {type:'choice',key,mode,site:this.source(t),target:v(2),contact:g('W',6613)};
   }
   if(this.decisions&&t.id===1&&op==='FlagOffJump'&&v(1)===867&&this.s.trueEndAvailable===undefined)return {type:'condition',condition:'prComplete',site:this.source(t)};
   if(op==='FlagOnJump'?g('F',v(1)):!g('F',v(1))){this.jump(t,t.script,v(2));return null;}}
  else if(op==='FlagOnWait'||op==='FlagOffWait'){const blocked=op==='FlagOnWait'?g('F',v(1)):!g('F',v(1));if(blocked){const key=x.name+':'+t.pc;this.stats.waits[key]=(this.stats.waits[key]||0)+1;t.wake=this.s.clock+1;return 'blocked';}}
  else if(op==='SetFlag'||op==='ResetFlag'){put('F',v(1),op==='SetFlag');if(v(1)===2600)put('W',6601,op==='SetFlag'?29:0);}
  else if(op==='CallRL'){this.jump(t,t.script,v(1),true);return null;}
  else if(op==='ScriptLoad')this.s.banks[v(1)]=v(2);
  else if(op==='CallFarRL'||op==='JumpFar'){const id=this.s.banks[v(1)],label=v(2);if(id===12&&label===325)this.s.events.push({type:'closeChoice'});if(id===1&&label>=23&&label%10===3)this.s.events.push({type:'expireRine',base:g('W',6655)});if(ir.scripts[id].name==='CLRFLG'&&label>=7&&label<=12){this.s.ending=label-7;t.dead=true;return {type:'end',ending:label-7};}this.jump(t,id,label,op==='CallFarRL');return null;}
  else if(op==='Switch')t.switch=v(1);
  else if(op==='Case'){if(t.switch===v(1)){this.jump(t,t.script,v(2));return null;}}
  else if(op==='Loop'){const k=t.script+':'+t.pc;t.loops??={};t.loops[k]=(t.loops[k]||0)+1;if(t.loops[k]<v(2)){this.jump(t,t.script,v(1));return null;}delete t.loops[k];}
  else if(op==='CreateThread'){
   const group=v(1),id=this.s.banks[v(2)],label=v(3),key=ir.scripts[id].name+':'+label;this.stats.threads[key]=(this.stats.threads[key]||0)+1;
   // Original interactive phone/audio UI service group 8 is replaced by the
   // explicit phone adapter; presentation group 6 retains actual final writes.
   if(group!==8){const child=this.thread(id,label,group);this.s.threads.push(child);t.param=child.id;child.param=t.id;}
  }else if(op==='ThreadControl'){if(v(2)===0){for(const child of this.s.threads)if(child.group===v(1)&&child.id!==t.id)child.dead=true;}else throw Error('ThreadControl mode '+v(2));}
  else if(op==='CopyThreadWork'){const src=v(1)?this.s.threads.find(x=>x.id===v(1)):t,dst=v(2)?this.s.threads.find(x=>x.id===v(2)):t;if(!src||!dst)throw Error('Missing thread work');for(let j=0;j<v(4);j++)this.put(dst,'T',v(3)+j,this.get(src,'T',v(3)+j));}
  else if(op==='Wait'||op==='Mwait'){t.wake=this.s.clock+Math.max(1,v(1));t.pc++;return 'blocked';}
  else if(op==='CalcMove'||op==='CalcAccel'){const dest=v(1),delta=v(2),at=v(3),duration=v(4);put('W',dest,Math.trunc(duration?op==='CalcMove'?delta*at/duration:delta*(2*at/duration-at*at/(duration*duration)):delta));}
  else if(op==='CalcSinL'||op==='CalcCosL')put('W',v(1),Math.trunc(v(4)+v(2)*Math[op==='CalcSinL'?'sin':'cos'](v(3)*2*Math.PI/65536)*65536));
  else if(op==='BGload'||op==='CHAloadAtlas'){const m=v(1);let slot=0;while(slot<8&&!(m&(1<<slot)))slot++;if(slot===8)throw Error('Image mask '+m);const id=v(2);put('W',(op==='BGload'?4507:5109)+slot*40,op==='BGload'?id:id&65535);if(op==='CHAloadAtlas'&&id>>>16)put('W',5112+slot*40,id>>>16);}
  else if(op==='BGswap'||op==='CHAswap')this.swap(t,v(1),v(2),op==='CHAswap');
  else if(op==='BGrelease'||op==='CHArelease'){const m=v(1);for(let slot=0;slot<8;slot++)if(m&(1<<slot))put('W',(op==='BGrelease'?4507:5109)+slot*40,65535);}
  else if(op==='GetSystemStatus')put('T',7,1);
  else if(op==='MovieMain'){put('W',6343,200);}
  else if(op==='SetSavePointMain')put('W',3373,100);
  else if(op==='GetControl'){/* Manual read advance; no desktop keyboard input. */}
  else if(op==='SG0ControlJump01'||op==='KeyOnJump2'||op==='ControlOnJump'){/* no pressed key; normal fallthrough */}
  else if(op.startsWith('SG0Phone'))this.phone(t,o);
  else if(op.startsWith('PlayMovie')||op==='PlayAlphaMovieLoopNoAudio'||op==='SG0Movie0A'){this.s.events.push({type:'movie',id:v(1),site:this.source(t)});}
  else if(presentation.has(op)){}
  else throw Error('Unknown instruction '+JSON.stringify({...this.source(t),op:o}));
  t.pc++;return null;
 }
 next({tickLimit=150000,instructionLimit=20000000}={}){
  const started=this.stats.instructions;
  for(let ticks=0;ticks<tickLimit;ticks++){
   for(let k=0;k<this.s.threads.length;k++){
    const t=this.s.threads[k];if(t.dead||t.wake>this.s.clock)continue;
    for(let steps=0;steps<20000;steps++){const r=this.step(t);if(r&&r.type)return r;if(r==='blocked'||t.dead)break;if(steps===19999)throw Error('Tight loop '+JSON.stringify(this.source(t)));}
   }
   if(this.s.threads[0].dead)return {type:'end'};
   if(this.stats.instructions-started>instructionLimit)throw Error('Instruction budget '+JSON.stringify(this.trace));
   // Native sound queues drain asynchronously. Voice/SE aren't exported by
   // this port; complete their queue-status words at the desktop tick boundary.
   for(let i=1300;i<1320;i++)this.put(this.s.threads[0],'W',i,65535);
   this.s.threads=this.s.threads.filter((t,i)=>i===0||!t.dead);this.s.clock++;
  }
  throw Error('Unresolved wait '+JSON.stringify(this.s.threads.filter(t=>!t.dead).map(t=>this.source(t))));
 }
 snapshot(){return copy(this.s);}
 answer(choice,yes){const t=this.s.threads[0];if(choice.type==='condition'){this.s.trueEndAvailable=!!yes;this.put(t,'F',867,yes);return;}
  if(yes){this.put(t,'F',2620,1);if(choice.mode===18){this.put(t,'W',6604,0);this.put(t,'W',6602,0);this.put(t,'F',2743,0);}else{this.put(t,'W',6604,1);this.put(t,'F',2743,0);this.put(t,'F',2740,0);}}
  else (this.s.phone.ignored??=[]).push(choice.key);
 }
}
module.exports={VM,ir};
if(require.main===module){const vm=new VM(),limit=Number(process.env.SG0_FRAMES||25),frames=[];let failure=null;
 try{for(let i=0;i<limit;i++){const f=vm.next({tickLimit:10000});frames.push(f);if(f.type==='end')break;}}catch(e){failure={message:e.message,trace:vm.trace};}
 const report={result:failure?'blocked':'desktop-trace-only',frames:frames.length,last:frames.slice(-3),failure,stats:vm.stats};fs.writeFileSync(path.join(root,'reports/desktop-trace.json'),JSON.stringify(report,null,2));fs.writeFileSync(path.join(root,'reports/desktop-checkpoint.json'),JSON.stringify(vm.snapshot()));
 console.log(JSON.stringify({result:report.result,frames:frames.length,failure,last:frames.slice(-1),instructions:vm.stats.instructions}));
 if(failure)process.exitCode=1;
}
