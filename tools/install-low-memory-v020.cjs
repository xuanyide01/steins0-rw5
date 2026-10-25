// Unchanged payloads; avoid ZIP inflate for all binary assets and most small text.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{createRequire}=require('module');
module.exports=async function(file,toolkit){
 const req=createRequire(path.join(path.resolve(toolkit),'package.json')),JSZip=req('jszip'),algorithm=req.resolve('@aiot-toolkit/packager/lib/signature/algorithm'),pem=path.join(path.dirname(algorithm),'../pem');
 const original=fs.readFileSync(file),zip=await JSZip.loadAsync(original,{checkCRC32:true});zip.comment='';const files=[],rows=[];let estimate=original.length;
 for(const [name,entry] of Object.entries(zip.files)){
  if(entry.dir){entry.options.compression='STORE';continue;}const data=await entry.async('nodebuffer'),compressed=entry._data.compressedSize;
  if(!Number.isFinite(compressed))throw Error('Missing pinned JSZip size');files.push({name,hash:crypto.createHash('sha256').update(data).digest()});
  const text=/\.(js|json|txt|css|ux)$/.test(name);entry.options.compression='STORE';estimate+=data.length-compressed;rows.push({name,entry,bytes:data.length,compressed,saving:data.length-compressed,text});
 }
 // Code/graph stay compact; add only enough smaller text streams to leave margin.
 const retained=new Set();function deflate(row){if(retained.has(row.name))return;retained.add(row.name);row.entry.options.compression='DEFLATE';estimate-=row.saving;}
 rows.filter(r=>r.text&&r.bytes>=65536).forEach(deflate);
 for(const row of rows.filter(r=>r.text&&!retained.has(r.name)).sort((a,b)=>b.saving-a.saving)){if(estimate<=24800000)break;deflate(row);}
 const unsigned=await zip.generateAsync({type:'nodebuffer',compression:'STORE',compressionOptions:{level:9}});
 const signed=require(algorithm).doSign(unsigned,files,fs.readFileSync(path.join(pem,'private.pem')),fs.readFileSync(path.join(pem,'certificate.pem')));if(signed.length>25000000)throw Error('Low-inflate package exceeds cap');fs.writeFileSync(file,signed);
 fs.writeFileSync(path.resolve(__dirname,'../reports/install-packaging-v020.json'),JSON.stringify({result:'prepared',sourceBytes:original.length,bytesBeforeR1:signed.length,allPayloadBytesUnchanged:true,storedFiles:rows.length-retained.size,deflatedFiles:retained.size,storedBinaryIncludes:['PNG','JPEG','WAV','MP3','TTF'],deflatedEntries:rows.filter(r=>retained.has(r.name)).map(({name,bytes,compressed})=>({name,bytes,compressed})),largestDeflatedBytes:Math.max(...rows.filter(r=>retained.has(r.name)).map(r=>r.bytes)),firmwareHeapNotMeasured:true},null,2));
};
