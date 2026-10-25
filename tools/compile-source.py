"""Parse SG0 disassembly and original glyph text into a desktop-only audit IR.
No code in this file is shipped as a watch-time SC3 interpreter.
"""
from pathlib import Path
import ast,re,json,struct,collections
ROOT=Path(__file__).resolve().parents[1];PROBE=ROOT.parent/'steins0-probe'
old=ROOT.parent/'steins-rw5/tools/compile-story.py'
module=ast.parse(old.read_text('utf8'));parts=[]
for node in module.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PREC','TOKEN') for t in node.targets):parts.append(ast.get_source_segment(old.read_text('utf8'),node))
 elif isinstance(node,ast.FunctionDef) and node.name in ('expression','split'):parts.append(ast.get_source_segment(old.read_text('utf8'),node))
exec('\n'.join(parts))
texts=json.loads((PROBE/'decoded-glyphs.json').read_text('utf8'));indexes=json.loads((PROBE/'indexes.json').read_text('utf8'));ids={Path(x['name']).stem:x['id'] for x in indexes['script.mpk']}
scripts={};counts=collections.Counter();errors=[];fallthrough=[]
for f in sorted((PROBE/'disasm-sc').glob('*.scs')):
 ident=ids[f.stem];ops=[];labels={};returns={};lines=f.read_text('utf8').splitlines();activeLabel=None
 for lineNo,line in enumerate(lines,1):
  m=re.fullmatch(r'(\*?)(\d+):',line)
  if m:
   (returns if m[1] else labels)[m[2]]=len(ops)
   if not m[1]:activeLabel=int(m[2])
   continue
  if 'error has occurred' in line:errors.append({'script':f.stem,'label':activeLabel,'line':lineNo,'message':line.split(' at ')[1].split(':')[0]})
  if not line.startswith('\t'):continue
  src=line.strip()
  if src.startswith('$'):
   m=re.fullmatch(r'(\$[WTF]\(.+?\))\s*(\+\+|--|<<=|>>=|[+\-*/%&|^]?=)\s*(.*?)\s*;',src)
   if not m:raise ValueError(f'Assignment {f.name}:{lineNo}: {src}')
   op=['set',expression(m[1]),m[2],1 if m[2] in ('++','--') else expression(m[3])]
  else:
   head,_,arg=src.partition(' ');counts[head]+=1
   if head in ['hex','db','dw','dd']:op=['data',activeLabel,src]
   else:
    try:args=[expression(x) for x in split(arg)]
    except Exception as e:
     errors.append({'script':f.stem,'label':activeLabel,'line':lineNo,'message':'operand: '+src});ops.append(['unparsed',src]);continue
    if head in ['MesSetMesScx','Mes2VSetMesScx','MesSSetMesScx','MesS2VSetMesScx']:
     i=args[-1];row=texts[f.stem][i];op=['text',row['speaker'],row['text'],i,head]
     effects=[]
     for token in row['tokens']:
      if token[0]==21:
       if token[1]!='290aa05a141400800000':raise ValueError('Unreviewed inline effect '+str(token))
       effects.append(['set',['F',90],'=',0])
     if effects:op.append(effects)
    else:op=[head]+args
  ops.append(op)
 data=(PROBE/'scripts'/f'{f.stem}.scx').read_bytes();first=struct.unpack_from('<I',data,12)[0];n=(first-12)//4;offsets=list(struct.unpack_from('<'+'I'*n,data,12));end=struct.unpack_from('<I',data,4)[0];memory={}
 # SG0 RINE tables also select labels indirectly through other tables. Keep
 # every label in the DESKTOP IR; no raw memory tables ship to the watch.
 for label in range(n):
  at=offsets[label];limit=min((x for x in offsets if x>at),default=end);memory[str(label)]=list(struct.unpack_from('<'+'i'*((limit-at)//4),data,at))
 for pos,op in enumerate(ops):
  if op[0] in ['SG0KeyboardJump01','SG0Control70','SG0Control71']:
   target=returns.get(str(op[-1]),labels.get(str(op[-1])));fallthrough.append({'script':f.stem,'pos':pos,'instruction':op,'target':target,'isFallthrough':target==pos+1})
 scripts[str(ident)]={'id':ident,'name':f.stem,'labels':labels,'returns':returns,'ops':ops,'memory':memory}
result={'format':2,'scripts':scripts,'banks':{'1':7,'4':9,'10':8,'6':11,'7':12,'9':0,'11':1,'2':13},'initial':[13,2]}
(PROBE/'vm-code.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),'utf8')
report={'result':'parsed-not-yet-semantic-validation','scripts':len(scripts),'ops':sum(len(x['ops']) for x in scripts.values()),'visibleFrames':counts['MesSetMesScx']+counts['Mes2VSetMesScx']+counts['MesSSetMesScx']+counts['MesS2VSetMesScx'],'opcodes':dict(counts),'decodeErrors':errors,'decodeErrorsInStory':[x for x in errors if x['script'].startswith('SG0')],'fallthroughInputInstructions':fallthrough,'nonFallthroughInputInstructions':[x for x in fallthrough if not x['isFallthrough']]}
(ROOT/'reports/source-compile.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['opcodes','decodeErrors','fallthroughInputInstructions','nonFallthroughInputInstructions']},ensure_ascii=False));print('decode errors',len(errors),'fallthrough input ops',len(fallthrough),'non-fallthrough',len(report['nonFallthroughInputInstructions']));print('non-fallthrough examples',report['nonFallthroughInputInstructions'][:5])

