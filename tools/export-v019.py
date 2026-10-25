from pathlib import Path
import json,hashlib,zipfile,shutil
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.9';p=R/'dist/com.codex.steins0.rw5.debug.0.1.9.rpk';a=audit(p)
n=json.loads((R/'native-test-results-v019/report.json').read_text('utf8'));m=json.loads((R/'reports/opening-v019-source.json').read_text('utf8'))
assert n['result']=='passed' and n['sha256']==a['sha256'];assert a['bytes']<25_000_000 and a['bytes']%16==1
assert m['allRetainedFramesSourceRelativeMseNoWorse'] and m['retainedFrameChecks']==663
unchanged=0;story=0
with zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.8-源码与检查.zip') as z:
 for f in z.namelist():
  if not f.startswith('src/common/'):continue
  if f in ['src/common/opening.js','src/common/media.txt'] or f.startswith('src/common/opening/') and f.endswith('.jpg'):continue
  assert (R/f).is_file() and z.read(f)==(R/f).read_bytes(),f
  unchanged+=1;story+=f.startswith('src/common/story/')
assert story==853
with zipfile.ZipFile(p) as z:
 for row in m['atlases']:assert hashlib.sha256(z.read('common/opening/'+row['file'])).hexdigest()==row['sha256']
diff={'baseVersion':'0.1.8','version':'0.1.9','unchangedCommonFiles':unchanged,'storyBlocksUnchanged':story,'plotGraphEngineFontsCGPortraitAudioAndSavesExact':True,'onlyOPClockSheetsAndUILayoutChanged':True,'packageEntries':a['entries'],'entriesUnchangedFromV018':a['entries']==2823,'sourceRelativeQualityNoWorseForRetainedFrames':663,'nativeSha256':a['sha256']}
for f,data in [('version-diff-v019.json',diff),('package-audit-v019.json',a)]:
 (R/'reports'/f).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》0.1.9 REDMI Watch 5 检查说明

作者xuanyide，Codex辅助实现与检查。2026-10-25。尚待本版实机验证。
安装包{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），低于25 MB；BIN/RPK相同。
SHA256：`{a['sha256']}`。

## OP停顿处理

0.1.8在手表表现为画面播放一段再停顿。旧实现每次切换1024×288八帧图片，缩放到1536×432，再改变横纵坐标；集中解码/缩放和UI更新可能造成周期性停顿。这是工程推断，没有实机剖析或崩溃栈，不能证明唯一原因。

新版目标6fps，每图4帧横向排列，源图1024×144、显示图层1536×216，256×144单帧和384×216居中显示范围保持。单图集RGBA589,824字节、显示预算1,327,104字节，均为旧版一半；每秒更新次数也减半，理论显示像素工作量约降至四分之一。这不是实机总RAM/FPS测量。只更新真正变化的图片路径/横坐标，不纵移；时间定位晚到直接选当前帧，不补绘一串旧帧，整数截止时间及代际保护避免边界空转和过期回调。

663个保留帧对应旧12fps的偶数帧，仍从原始PNG重建。JPEG质量35提高至45；逐帧对同一原PNG计算MSE，新版每一帧均未增加，平均55.8456降到46.1589。没有继续降分辨率或空间画质，也不是宣称新旧JPEG逐像素相同。时间采样减至6fps是明确取舍，实际观感需上机确认，不能保证看起来像12fps。

原OP音轨与110.4768秒时长不变。序章跳章停OP、点击跳过、第一章CG接正文、EXTRA独立观看、声音开关、后台暂停续播及旧存档逻辑保持。

## 安装反馈与封装

用户报告0.1.8第一次安装失败并导致手表重启，重启后第二次成功。已如实记录，未将0.1.8标成稳定通过。0.1.9包体减少1,733,312字节、图集仍166张、总包条目2823未增，保持相同包名、证书及DEFLATE/R1封装；降低文件负担不等于已根治安装重启。没有修改真实手表或建议为测试随意恢复出厂设置。

## 检查范围

- 最终包通过官方Vela模拟器安装及系统冷启；完整有声剧情OP、静音EXTRA、点击/重复跳过、章标题接续、旧0.1.0存档已操作检查和截图核对。模拟器不是实机性能保证。
- 全部663个保留帧质量对照，166张成品文件/包内摘要，时钟完整帧数/单定时器/迟到不补帧/过期回调/后台/销毁检查通过。
- 原六路线、11关键决策、35回复窗口、105次回复发送、108跳章位置及存档/UI/媒体检查通过。
- 与0.1.8源码包逐字节比较，853剧情块、剧情图与引擎、CG/立绘/字体、标题动画/音乐、OP音轨、存档和手机回复资源保持；只改OP图片、时钟/显示布局及相关元数据。原有30栏位/状态3/外层2保持。
- ZIP CRC、内外签名、全部文件摘要通过。原生报告native-test-results-v019/，质量reports/opening-v019-source.json，时钟reports/opening-clock-v019.json。

蓝牙传输后仍需等待解包登记，更新前备份重要存档。若仍明显卡顿，可先关闭CONFIG声音对照，或点击跳过OP继续游戏；若安装再次触发重启，请先停止重复安装并记录步骤。不保证固件不会重启。保留旧版，不新输出独立视频/音轨，不发邮件、不上传GitHub。
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
 for f in ['runtime-tests.json','rine-tests-v013.json','skip-tests-v016.json','ui-v019-tests.json','media-tests.json','opening-v019-source.json','opening-clock-v019.json','opening-pixels-v019.json','package-audit-v019.json','version-diff-v019.json']:z.write(R/'reports'/f,'reports/'+f)
 for f in sorted((R/'native-test-results-v019').iterdir()):
  if f.suffix in ['.png','.json']:z.write(f,f.relative_to(R).as_posix())
 for f in ['src/common/opening.js','src/pages/index/index.ux']:z.write(R/'reports/before-v019'/f,'reports/before-v019/'+f)
 z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<25_000_000
files=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
 f=O/(name+ext);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v019.json').write_text(json.dumps({'version':'0.1.9','physicalDeviceTested':False,'files':files},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(files,ensure_ascii=False,indent=2))
