"""Reuse ATRI's lossless scanline/DEFLATE search; assert pixels, palette and alpha exact."""
from pathlib import Path
import concurrent.futures,hashlib,importlib.util,json,sys,shutil,struct,zlib,io
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v014';B.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('atri_lossless',R/'tools/png-lossless-reference.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sys.path.insert(0,str(R.parent/'anemoi-rw5-rebuild/tools/build-deps'))
import zopfli.zlib
def optimize(item):
    name,data,result=mod.optimize(item);before=data;at=8;parts=[]
    while at<len(data):
        length=struct.unpack_from('>I',data,at)[0]
        if data[at+4:at+8]==b'IDAT':parts.append(data[at+8:at+8+length])
        at+=12+length
    stream=zlib.decompress(b''.join(parts));packed=zopfli.zlib.compress(stream,numiterations=3);candidate=mod.replace_idat(data,packed)
    if len(candidate)<len(data):data=candidate;result['method']+='+zopfli3'
    assert Image.open(io.BytesIO(before)).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes()
    result.update(after=len(data),saved=result['before']-len(data),pixelPaletteAlphaExact=True)
    return name,data,result
sample='--sample' in sys.argv
paths=sorted((R/'src/common').rglob('*.png'))
if sample:paths=paths[::max(1,len(paths)//20)][:20]
items=[(p.relative_to(R).as_posix(),p.read_bytes()) for p in paths];rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for index,(name,data,result) in enumerate(pool.map(optimize,items)):
        if not sample and result.get('saved',0)>0:
            target=R/name;backup=B/name;backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists():shutil.copyfile(target,backup)
            target.write_bytes(data)
        rows.append(dict(path=name,sha256=hashlib.sha256(data).hexdigest(),**result))
        if index%200==0:print('PNG',index,'/',len(items),flush=True)
report={'result':'passed','sampleOnly':sample,'reference':'ATRI/tools/compress-portraits-lossless.py','files':len(rows),'beforeBytes':sum(r['before'] for r in rows),'afterBytes':sum(r['after'] for r in rows),'savedBytes':sum(r['before']-r['after'] for r in rows),'paletteAlphaAndPixelsExact':True,'rows':rows}
(R/'reports'/('lossless-sample-v014.json' if sample else 'lossless-png-v014.json')).write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
