const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const R=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(R,p),'utf8'));
let code=fs.readFileSync(path.join(R,'src/common/glyph-widths.js'),'utf8').replace(/export /g,'');
code+='\n'+fs.readFileSync(path.join(R,'src/common/text-font.js'),'utf8').replace(/^import .*;\r?$/gm,'').replace(/export /g,'');
const {cleanText,wrapText}=Function(code+';return {cleanText,wrapText};')();
const g=read('src/common/graph.txt'),seen=new Set(),issues=[],pua=new Set();let frames=0,wrapped=0,maxLine=0;
function check(raw,site){const s=cleanText(raw);for(const ch of s)if(/[\uE000-\uF1FF]/.test(ch))pua.add(ch.charCodeAt(0));
 const spaced=s.match(/\b[A-Za-z](?: [A-Za-z]){2,}\b/g),cjk=s.match(/[\u3040-\u9FFF\uE0E8-\uF1FF] +[\u3040-\u9FFF\uE0E8-\uF1FF]/g);
 if(spaced||cjk)issues.push({site,spaced,cjk});
 return s;}
for(const [i,t] of g.titles.entries())check(t,'title:'+i);
for(const n of Object.values(g.nodes))for(const c of n.chunks){if(seen.has(c.file))continue;seen.add(c.file);for(const f of read('src/common/story/'+c.file).frames){frames++;const s=check(f[1],f[5]);const w=wrapText(s,384,28).split('\n');maxLine=Math.max(maxLine,w.length);if(w.length>4)wrapped++;}}
const a=read('reports/package-audit-v011.json'),report={result:issues.length?'review-needed':'passed',uniqueFrames:frames,sourceChunks:seen.size,remainingSpacingExamples:issues.slice(0,50),largeFontParagraphsOverFourLines:wrapped,maxLargeFontLines:maxLine,puaGlyphs:[...pua].sort((a,b)=>a-b),packageSha256:a.sha256};
fs.writeFileSync(path.join(R,'reports/presentation-audit-v011.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({...report,puaGlyphs:report.puaGlyphs.length}));assert.equal(issues.length,0);
