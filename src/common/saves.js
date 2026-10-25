import {checkpoint,restore,chapterTitle,getGraph} from './engine.js';
import {textFont,cleanText} from './text-font.js';
import {worldlineFor} from './worldline.js';
export const SLOT_COUNT=30;
export const LEGACY_KEY='steins0_rw5_unused_legacy';
export const SLOT_INDEX_KEY='steins0_rw5_slot_index_v1';
export function slotKey(index){if(!Number.isInteger(index)||index<0||index>=30)throw Error('栏位无效');return 'steins0_rw5_slot_v2_'+(index+1);}
export function decodeSave(raw){if(!raw)return null;const s=JSON.parse(raw);if(s.version!==2)throw Error('存档版本不兼容');return {version:2,state:restore(s.state,true),savedAt:s.savedAt,sceneMode:s.sceneMode};}
export function createSave(state,sceneMode,savedAt){return {version:2,state:checkpoint(state),sceneMode,savedAt};}
export function slotMeta(saved){
 const s=saved.state,g=getGraph();if(saved.version!==2||!s||s.format!==3||!g.nodes[s.chapter]||!Number.isInteger(s.cursor)||s.cursor<0||s.cursor>g.nodes[s.chapter].count)throw Error('存档位置无效');
 return {version:2,state:{format:3,chapter:s.chapter,cursor:s.cursor,title:String(s.title||'').slice(0,160),text:String(s.text||'').slice(0,96),worldline:s.worldline},savedAt:saved.savedAt,sceneMode:saved.sceneMode};
}
// List metadata never restores/clones the story, mail, flags or reply history.
export function decodeSlotMeta(raw){return raw?slotMeta(JSON.parse(raw)):null;}
export function decodeSlotIndex(raw){
 if(!raw)return {};const data=JSON.parse(raw);if(data.version!==1||!data.slots||typeof data.slots!=='object')return {};const out={};
 for(let i=0;i<SLOT_COUNT;i++){if(!Object.prototype.hasOwnProperty.call(data.slots,i))continue;const meta=data.slots[i];if(meta===null)out[i]=null;else if(meta&&meta.invalid)out[i]={invalid:true};else try{out[i]=slotMeta(meta);}catch(e){}}
 return out;
}
function two(i){return ('0'+i).slice(-2);}
export function slotRow(index,saved){
 const row={index,number:index+1,title:'存档 '+two(index+1),meta:'空栏位',preview:'',occupied:!!saved,metaFont:'sans-serif',previewFont:'sans-serif'};
 if(!saved)return row;if(saved.invalid){row.meta='存档无法读取';return row;}
 const d=new Date(saved.savedAt);row.meta=chapterTitle(saved.state)+' · '+two(d.getMonth()+1)+'/'+two(d.getDate())+' '+two(d.getHours())+':'+two(d.getMinutes());
 row.preview=saved.sceneMode==='choice'?'正在选择关键剧情操作':cleanText(saved.state.text||'章节开头').slice(0,24);row.metaFont=textFont(row.meta);row.previewFont=textFont(row.preview);return row;
}
