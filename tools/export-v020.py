from pathlib import Path
import json,zipfile,hashlib,shutil
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.2.0';p=R/'dist/com.codex.steins0.rw5.debug.0.2.0.rpk';a=audit(p)
n=json.loads((R/'native-test-results-v020/report.json').read_text('utf8'));analysis=json.loads((R/'reports/install-analysis-v020.json').read_text('utf8'));assert n['result']=='passed' and n['sha256']==a['sha256'];assert a['bytes']<25_000_000 and a['bytes']%16==1
assert analysis['runtimeCommonBytesExactExceptOfflineMetadata'] and analysis['after']['deflatedFiles']==45;assert (R/'src/common/assets.txt').exists()
with zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.10-源码与检查.zip') as z:
 for f in z.namelist():
  if f.startswith('src/common/') or f=='src/pages/index/index.ux':assert z.read(f)==(R/f).read_bytes(),f
check=f'''# 《命运石之门0》REDMI Watch 5 0.2.0：低解压封装

作者xuanyide，Codex辅助完成实现及检查。2026-10-25。本版实机安装仍待确认。
安装包{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），小于25,000,000字节。BIN/RPK相同。
SHA256：`{a['sha256']}`。

## 本次处理

用户反馈0.1.10第一次安装触发手表重启，第二次没有图标，重置后成功。本版没有实机崩溃栈，不认定唯一根因，也不建议把反复重置当常规安装步骤。

此前全部2769个非目录文件都走外层ZIP DEFLATE。0.2.0将PNG/JPEG、PCM WAV、MP3、TTF及大部分小文本改为STORE直接存储，保留45个文本DEFLATE以控制25 MB上限；无需inflate的非目录文件2723个。需要DEFLATE展开的总字节25,186,578→731,974；这衡量累计工作量，不是峰值RAM。最大DEFLATE文件4,621,524→249,621字节。目录/资源条目总数2878→2877，只有运行时不读取的转换清单common/assets.txt被排除出包；源文件在编译结束后恢复，历史转换工具仍可用。

包体由21.29增到24.80 MB，是取消外层压缩的代价；游戏资源、画质和音频没有重编码。8fps、884帧OP、标题音乐、剧情、CG/立绘/字体、手机回复、保存/加载与UI代码保持，原包名/证书、R1尾部封装和存档外层2/状态3/30栏位不变。

## 内存边界

参考[open-vela安装代码](https://github.com/open-vela/frameworks_system_utils_uv/blob/dev/src/app_verify.c)及[Kconfig](https://github.com/open-vela/frameworks_system_utils_uv/blob/dev/Kconfig)，解包输出缓冲按单文件大小与配置分块上限取较小值，并非一次把整个安装包展开。公开默认分块512000字节。新版最大压缩文件的输出块上限由512000降到249621字节，但STORE大文件仍可能使用512000字节输出缓冲；不能把压缩文件上限当整个安装过程峰值，更不能把文件大小缩减比例当实机RAM降幅。

本版明确减少了大量inflate调用和分配点，让图片、音频和字库直接落盘；手表固件具体实现、剩余堆和碎片状态未知。没有修改固件或绕过验签，也没有证据保证首次安装绝不重启。

## 检查

- 与0.1.10包逐文件比较，除清单移出、版本/签名/构建元数据变化外，全部common运行资源字节相同；完整UI及源码common也相同。
- RPK ZIP CRC、内外签名、全部文件摘要通过。STORE/DEFLATE统计和单文件边界见reports/install-analysis-v020.json与install-packaging-v020.json。
- 准确SHA在官方Vela模拟器成功安装并完整系统冷启，标题/PCM音乐、OP图片及MP3、点击跳过接原章节CG/正文、原0.1.0存档n0:1恢复通过。模拟器不是实机固件，也没有测量实机安装峰值内存。
- npm test通过六路线、11关键决策、35回复窗口、105次回复发送、108跳章、完整884帧时钟和旧UI/存档/媒体检查。OP/标题媒体内容未变，本轮不重复整段及长期耐久测试；沿用0.1.10的完整OP证据并核对字节一致。

更新前备份重要进度。蓝牙传输结束后仍需等待解包登记；如再次重启或不出现图标，先停止重复安装并记录工具提示和步骤。没有在真实手表卸载/重置或清除存档。旧交付保留，不上传GitHub、不发邮件、不新输出视频/音轨。
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
 for f in ['runtime-tests.json','rine-tests-v013.json','skip-tests-v016.json','ui-v0110-tests.json','media-tests.json','opening-clock-v0110.json','install-analysis-v020.json','install-packaging-v020.json','package-audit-v020.json']:z.write(R/'reports'/f,'reports/'+f)
 for f in sorted((R/'native-test-results-v020').iterdir()):
  if f.suffix in ['.png','.json']:z.write(f,f.relative_to(R).as_posix())
 z.write(R/'reports/before-v020/tools/build.cjs','reports/before-v020/tools/build.cjs');z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<25_000_000
files=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
 f=O/(name+ext);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v020.json').write_text(json.dumps({'version':'0.2.0','physicalDeviceTested':False,'files':files},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(files,ensure_ascii=False,indent=2))
