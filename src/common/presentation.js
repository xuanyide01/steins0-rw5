// Display preferences stay outside the story/save format.
export const FONT_SIZES=[22,24,28];
export const TEXT_MODES=['character','sentence','instant'];
export function settingsFrom(saved){
 const value=saved||{},font=Number(value.font);
 return {font:font<=22&&font>0?22:font>=26?28:24,
  textMode:TEXT_MODES.indexOf(value.textMode)>=0?value.textMode:value.textSpeed===0?'instant':'character',
  autoSpeed:[0,1,2].indexOf(value.autoSpeed)>=0?value.autoSpeed:1,
  sound:value.sound!==false,animation:value.animation!==false};
}
export function fontName(size){return size<=22?'小':size>=28?'大':'中';}
export function textModeName(mode){return mode==='sentence'?'逐句':mode==='instant'?'即时':'逐字';}
export function pageLabel(page,total){return '第 '+(page+1)+' 页，共 '+Math.max(1,total)+' 页';}
export function sentenceStops(text){
 const value=String(text||''),stops=[],closing='」』】）》）”’\"\'';
 for(let i=0;i<value.length;i++){
  const ch=value.charAt(i),next=value.charAt(i+1);
  if('。！？!?'.indexOf(ch)<0&&!(ch==='.'&&(!next||/\s/.test(next))))continue;
  while(i+1<value.length&&('。！？!?'.indexOf(value.charAt(i+1))>=0||closing.indexOf(value.charAt(i+1))>=0))i++;
  while(i+1<value.length&&/\s/.test(value.charAt(i+1)))i++;
  stops.push(i+1);
 }
 if(!stops.length||stops[stops.length-1]!==value.length)stops.push(value.length);
 return stops;
}
