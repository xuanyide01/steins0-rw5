from pathlib import Path
import json,hashlib,zipfile,shutil
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.10';p=R/'dist/com.codex.steins0.rw5.debug.0.1.10.rpk';a=audit(p)
n=json.loads((R/'native-test-results-v0110/report.json').read_text('utf8'));m=json.loads((R/'reports/opening-v0110-source.json').read_text('utf8'))
assert n['result']=='passed' and n['sha256']==a['sha256'];assert a['bytes']<25_000_000 and a['bytes']%16==1
assert m['targetFPS']==8 and m['targetFrames']==884 and m['samePerImageBudgetAsTestedSixFPS'] and m['allCommonFramesSourceRelativeMseNoWorse']
unchanged=0;story=0
with zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.9-源码与检查.zip') as z:
 for f in z.namelist():
  if not f.startswith('src/common/'):continue
  if f in ['src/common/opening.js','src/common/media.txt'] or f.startswith('src/common/opening/') and f.endswith('.jpg'):continue
  assert (R/f).is_file() and z.read(f)==(R/f).read_bytes(),f
  unchanged+=1;story+=f.startswith('src/common/story/')
assert story==853
with zipfile.ZipFile(p) as z:
 for row in m['atlases']:assert hashlib.sha256(z.read('common/opening/'+row['file'])).hexdigest()==row['sha256']
assert (R/'src/pages/index/index.ux').read_bytes()==(R/'reports/before-v0110/src/pages/index/index.ux').read_bytes()
diff={'baseVersion':'0.1.9','version':'0.1.10','unchangedCommonFiles':unchanged,'storyBlocksUnchanged':story,'UIUnchanged':True,'plotEngineSavesCGFontsPortraitsAudioAndTitleExact':True,'onlyOPRateSheetsMetadataAndAppVersionChanged':True,'commonFramesQualityNoWorse':m['commonTemporalFramesChecked'],'nativeSha256':a['sha256']}
for f,data in [('version-diff-v0110.json',diff),('package-audit-v0110.json',a)]:
 (R/'reports'/f).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.10：8fps试验版

作者xuanyide，Codex辅助实现及检查。2026-10-25。
用户已确认0.1.9的6fps OP“现在可以正常播放”；本版8fps尚待实机确认。

安装包{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），低于25 MB。BIN/RPK相同。
SHA256：`{a['sha256']}`。

## 调整范围

目标更新率从6fps适度增加到8fps，更新间隔约167ms变为125ms；保持单图片、4帧横排、仅变化时写属性、单定时器和迟到不补绘机制。原画面256×144、图集1024×144、显示图层1536×216和居中视口384×216均保持，单次图片/纹理预算不增加，每秒更新和读取次数约增加三分之一。并未恢复旧12fps的两行大图集。

完整OP110.4768秒，共884帧/221张图集。新中间帧直接从原作解码PNG取样，不使用生成式插帧。JPEG至少质量45，其中153图为45、68图为50；221个共同时间点与6fps版对相同原图比较，MSE逐一未增加。与旧版没有相同时间采样的新增帧不作逐帧等价声称。原音轨逐字节保持。

包体比6fps版增加959,440字节，图集增加55张，总ZIP条目2878；保持相同包名、证书及DEFLATE/R1封装。0.1.9安装包及交付文件保留用于对照。6fps正常播放的反馈未提供固件、时长或首次安装是否成功，不代表所有功能/长期稳定性均已证明。

## 验证

- 最终准确摘要包通过官方Vela安装及系统冷启，完整有声OP、第一章CG/正文接续、EXTRA跳过、约20秒静音播放并退出、重复打开/跳过及原0.1.0存档恢复检查；8fps实机观感待测。
- 单时钟完整884帧/221文件、水平移动、后台暂停/续播、晚到不补绘、过期回调、结束/跳过、旧档迁移与存档返回检查通过。新时钟完整播放的最小定时延迟102ms，无1ms追赶空转。
- 六路线、11关键决策、35回复窗口、105次回复发送、108跳章及原UI/媒体检查通过。图集包内摘要、ZIP CRC、内外签名及全部文件摘要通过。
- 与0.1.9逐字节比较，完整UI、853剧情块、剧情图/引擎、CG/立绘/字库、全部音频、标题动画及存档逻辑保持。只修改OP帧序列、目标帧率和应用版本/媒体元数据。存档外层2/状态3、30栏位key保持。
- 报告reports/opening-v0110-source.json、opening-clock-v0110.json、ui-v0110-tests.json、package-audit-v0110.json及native-test-results-v0110/。模拟器观察不是实机FPS、RAM或耐久测试。

蓝牙传输完成后仍需等待解包登记；更新前备份重要进度。保留已通过播放测试的6fps版供对照。没有为本版修改真实手表、清除用户存档、上传GitHub、发邮件或输出独立OP文件。
'''
(O/(name+'-检查说明.md')).write_text(check,encoding='utf8')
for ext in ['bin','rpk']:
 dst=O/(name+'.'+ext)
 if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==a['sha256']
 shutil.copyfile(p,dst)
shutil.copyfile(R/'README.md',O/(name+'-使用说明.md'))
archive=O/(name+'-源码与检查.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for folder in ['src','tools']:
  for f in sorted((R/folder).rglob('*')):
   if f.is_file() and not any(x in f.relative_to(R).parts for x in ['node_modules','__pycache__']) and f.suffix not in ['.pyc','.log']:z.write(f,f.relative_to(R).as_posix())
 for f in ['README.md','WORK_PROGRESS.md','LICENSE','package.json']:z.write(R/f,f)
 for f in ['runtime-tests.json','rine-tests-v013.json','skip-tests-v016.json','ui-v0110-tests.json','media-tests.json','hardware-feedback-v019.json','opening-v0110-source.json','opening-clock-v0110.json','opening-pixels-v0110.json','package-audit-v0110.json','version-diff-v0110.json']:z.write(R/'reports'/f,'reports/'+f)
 for f in sorted((R/'native-test-results-v0110').iterdir()):
  if f.suffix in ['.png','.json']:z.write(f,f.relative_to(R).as_posix())
 z.write(R/'reports/before-v0110/src/common/opening.js','reports/before-v0110/src/common/opening.js');z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<25_000_000
files=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
 f=O/(name+ext);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v0110.json').write_text(json.dumps({'version':'0.1.10','physicalDeviceTested':False,'files':files},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(files,ensure_ascii=False,indent=2))
