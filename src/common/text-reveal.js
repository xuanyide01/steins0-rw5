// One row plan per paragraph; keep rendered rows and IDs stable while revealing.
export function planTextRows(text,generation){
 const rows=[],ranges=[];let offset=0;
 for(const value of String(text||'').split('\n')){rows.push({id:'text:'+generation+':'+rows.length,text:''});ranges.push({start:offset,text:value});offset+=value.length+1;}
 return {rows,ranges};
}
export function revealTextRows(rows,ranges,length){
 let changed=0;
 for(let i=0;i<ranges.length;i++){const r=ranges[i],value=r.text.slice(0,Math.max(0,length-r.start));if(rows[i].text!==value){rows[i].text=value;changed++;}}
 return changed;
}
export function nextGlyphEnd(text,index){
 let end=index;
 // Newline is layout, not a character to wait for. Preserve surrogate pairs.
 while(end<text.length&&text.charAt(end)==='\n')end++;
 if(end<text.length){const code=text.charCodeAt(end++);if(code>=0xd800&&code<=0xdbff&&end<text.length){const low=text.charCodeAt(end);if(low>=0xdc00&&low<=0xdfff)end++;}}
 return end;
}
