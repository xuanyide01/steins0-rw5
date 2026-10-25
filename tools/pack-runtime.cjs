const fs=require('fs'),path=require('path'),vmContext=require('vm'),{VM,ir}=require('./desktop-vm.cjs');
const R=path.resolve(__dirname,'..'),O=path.join(R,'src/common'),P=path.resolve(R,'../steins0-probe'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,x)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(x));};
const g=read(path.join(R,'reports/raw-graph.json')),raw=read(path.join(R,'reports/raw-visuals.json')),assets=read(path.join(O,'assets.txt')),texts=read(path.join(P,'decoded-glyphs.json'));
const clamp=x=>Math.max(0,Math.min(1,x)),px=432/1920,sc=432/1280;
const views=raw.map(view=>{
 const layers=[];for(const row of view[0]){const [slot,...b]=row,id=b[7];if(id===65535)continue;let image=id<0?'color'+id:'bg'+id,info=assets.backgroundGeometry[id]||{size:[1920,1080]},w=info.size[0]*px,h=info.size[1]*px,left=-b[0]*sc,top=-b[1]*sc;
  if([2,6].includes(b[9])){w*=b[4]/1000||1;h*=b[4]/1000||1;left=b[0]*sc-w/2;top=b[1]*sc-h/2;}
  if(b[9]===1){image=assets.backgroundCrops[[id,b[2],b[3],b[5],b[6]].join(':')]||image;w=432;h=243;left=top=0;}
  let alpha=clamp(b[13]/256);if(b[11]===1)alpha*=clamp(b[10]/256);
  if([15,16].includes(b[11]))image=assets.backgroundMasks[[id,b[11],b[14],b[10],b[15]].join(':')]||image;
  if(alpha>0)layers.push([image,Math.round(left),Math.round(top),Math.round(w),Math.round(h),Math.round(alpha*1000),b[8]]);
 }
 for(const row of view[1]){const [slot,...b]=row,id=b[9],face=b[12];if(id===65535||!b[7])continue;const image=assets.portraits[id+':'+face];if(!image)throw Error('Portrait missing '+id+':'+face);const geometry=assets.portraitGeometry[image],sx=b[5]/1000||1,sy=b[6]/1000||1;let alpha=clamp(b[7]/256);if(b[15]===1)alpha*=clamp(b[14]/256);if(alpha>0)layers.push([image,Math.round(b[0]*sc+geometry.origin[0]*px*sx),Math.round(b[1]*sc+geometry.origin[1]*px*sy),Math.round(geometry.size[0]*px*sx),Math.round(geometry.size[1]*px*sy),Math.round(alpha*1000),b[10]]);}
 return layers.sort((a,b)=>a[6]-b[6]);
});
// Original phone text tables contain uint16 SCX string IDs.
const data=fs.readFileSync(path.join(P,'scripts/_phone.scx')),first=data.readUInt32LE(12),n=(first-12)/4,ptr=Array.from({length:n},(_,i)=>data.readUInt32LE(12+i*4)),groups={};
for(let label=8;label<57;label++){const end=Math.min(...ptr.filter(p=>p>ptr[label]));const ids=[];for(let at=ptr[label];at+1<end;at+=2){const id=data.readUInt16LE(at);if(id>=texts._phone.length)throw Error('Invalid phone text table '+label+':'+id);ids.push(id);}groups[label]=ids;write(path.join(O,'phone',label+'.txt'),ids.map(id=>texts._phone[id].text));}
const names=Object.fromEntries(Array.from({length:16},(_,i)=>[i,texts._phone[136+i]?.text||'']));
const contacts=[1,2,5,4,7,6,9,8,11,10],contactNames=Object.fromEntries(contacts.map((id,i)=>[id,texts._phone[[114,116,118,120,122,124,126,128,130,132][i]].text]));
function callback(event){
 const [script,label]=event.callback,key=[script,label,event.base,event.contact].join('-');const machine=new VM(),t=machine.s.threads[0];machine.put(t,'W',6655,event.base);machine.put(t,'W',1501,event.contact);machine.s.phone.contact=event.contact;machine.jump(t,script,label);t.stack=[];
 for(let guard=0;guard<1000;guard++){if(ir.scripts[t.script].ops[t.pc][0]==='SG0Phone0E')break;machine.step(t);if(guard===999)throw Error('RINE reply table guard '+key);}
 const replies=[];for(const item of machine.s.phone.replies||[]){const m=new VM(machine.snapshot()),ct=m.s.threads[0];m.jump(ct,item.script,item.label);ct.stack=[];const sequence=[];
  for(let guard=0;guard<1000;guard++){const op=ir.scripts[ct.script].ops[ct.pc];if(op[0]==='SG0Phone0B')break;if(op[0]==='SG0Phone0F')sequence.push({sender:m.val(op[1],ct),outgoing:m.val(op[1],ct)===0,stamp:!!m.val(op[2],ct),id:m.val(op[3],ct),contact:event.contact});m.step(ct);if(guard===999)throw Error('RINE reply body guard '+key);}
  replies.push({id:item.id,sequence});
 }
 write(path.join(O,'reply',key+'.txt'),{base:event.base,contact:event.contact,stampChoices:!!machine.s.phone.replyStamp,replies});return key;
}
let block=0,maxBytes=0,maxLayers=0;const blockMemo=new Map();
function pack(rows){const parts=[];let current=[],local=[],mapping=new Map();
 function flush(){if(!current.length)return;const value={frames:current,views:local},text=JSON.stringify(value);if(Buffer.byteLength(text)>28000)throw Error('Oversized chunk');let file=blockMemo.get(text);if(!file){file=Math.floor(block/40)+'/'+block%40+'.txt';block++;blockMemo.set(text,file);write(path.join(O,'story',file),value);}maxBytes=Math.max(maxBytes,Buffer.byteLength(text));parts.push({file,count:current.length});current=[];local=[];mapping=new Map();}
 for(const input of rows){if(current.length>=40)flush();let row=input.slice();row[4]=g.titles.indexOf(row[4]);if(!mapping.has(row[2])){mapping.set(row[2],local.length);local.push(views[row[2]]);}row[2]=mapping.get(row[2]);current.push(row);maxLayers=Math.max(maxLayers,...local.map(v=>v.length));if(Buffer.byteLength(JSON.stringify({frames:current,views:local}))>24000&&current.length>1){current.pop();flush();row=input.slice();row[4]=g.titles.indexOf(row[4]);row[2]=0;current.push(row);local=[views[input[2]]];mapping.set(input[2],0);}}
 flush();return parts;
}
const replyKeys=new Set();
for(const node of Object.values(g.nodes)){
 if(node.choice){node.choice.contact=node.choice.contact===0?3:node.choice.contact;if(node.choice.kind==='call'){if(node.choice.mode===13){node.choice.contact=3;node.choice.heading='Amadeus 来电';}else node.choice.heading=names[node.choice.contact]||'来电';}}
 const rows=node.chunks.flatMap(c=>read(path.join(R,'reports/raw-story',c.file)));node.breaks=[];let previous='';rows.forEach((row,i)=>{if(row[6]!==previous){node.breaks.push(i);previous=row[6];}});node.chunks=pack(rows);
 node.events=node.events.filter(e=>e.type!=='opening'&&(e.type!=='message'||e.sender!==undefined)).map(e=>{if(e.type!=='rineReply')return e;const key=callback(e);replyKeys.add(key);return {at:e.at,type:'rineReply',key,base:e.base,contact:e.contact};});
}
const contactNumbers=Object.fromEntries(contacts.map((id,i)=>[id,texts._phone[115+i*2].text]));g.phone={names,contacts,contactNames,contactNumbers};write(path.join(O,'graph.txt'),g);write(path.join(R,'reports/runtime-resources.json'),{watchRunsOriginalVM:false,singleCachedChunk:true,maxChunkBytes:maxBytes,maxLayers,graphBytes:fs.statSync(path.join(O,'graph.txt')).size,blocks:block,replies:replyKeys.size,openingIncluded:false});
console.log('PACKED',block,'blocks',maxBytes,'bytes',maxLayers,'layers',replyKeys.size,'reply sets');
