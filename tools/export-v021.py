from pathlib import Path
import json,zipfile,hashlib,shutil
from rpk_signature import audit

R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs'
name='命运石之门0-REDMIWatch5-0.2.1';p=R/'dist/com.codex.steins0.rw5.debug.0.2.1.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v021/report.json').read_text('utf8'))
compat=json.loads((R/'reports/compatibility-v021.json').read_text('utf8'))
hardware_path=R/'reports/hardware-feedback-v021.json'
hardware=json.loads(hardware_path.read_text('utf8')) if hardware_path.exists() else {'physicalDeviceTested':False}
assert native['result']=='passed' and native['sha256']==a['sha256']
assert a['bytes']<25_000_000 and a['bytes']%16==1
assert a['certificateSha256']=='4e8e1ee24968b0dad6d0956a7e14d848b38b22a203f39c389a45d8737bdc4585'
assert compat['allRuntimeCommonBytesExactWith020'] and compat['storyBlocksIdentical']==853
assert compat['binaryFilesAllStored'] and compat['deflatedFiles']==45 and (R/'src/common/assets.txt').exists()
reports=['clear-awards-v021-source.json','clear-awards-v021-tests.json','ui-v021-tests.json',
         'runtime-tests.json','rine-tests-v013.json','skip-tests-v016.json','media-tests.json',
         'opening-clock-v0110.json','compatibility-v021.json','package-audit-v021.json']
for f in reports:
 data=json.loads((R/'reports'/f).read_text('utf8'))
 assert data.get('result','passed')=='passed',f
check=f'''# 《命运石之门0》REDMI Watch 5 0.2.1：通关记录修复

作者：xuanyide；Codex辅助完成分析、实现与验证。2026-10-25。

安装包：{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），小于25,000,000字节。BIN与RPK字节相同。
SHA256：`{a['sha256']}`。

## 修复原因与行为

用户通过跳章完成《无限远点的牵牛星》及《交差坐标的星尘》后，通关列表只记录后者。核对本地原作SC3 CLRFLG结算脚本发现：结束编号5除设置F806外，还从结局表读取附加标记804，设置F804；对应同时登记《交差坐标的星尘》与《无限远点的牵牛星》。旧移植仅登记最后一个结局，正常阅读也存在同样遗漏，并非跳章特有。

0.2.1统一补齐该结算依赖：完成真结局时两项均为“已完成”；仅进入章节不会提前结算；单独完成《无限远点的牵牛星》不会反向解锁真结局，其他结局不会被无关解锁。原来的路线条件、关键电话和回复窗口没有修改。

启动时自动修复旧版已记录真结局、却漏记前章的全局进度，并写回原键；不需要重打。原有其他通关标记、世界线数值和设置保留；加载旧存档时也补齐同一规则。迁移仅增加应有记录，不清除原记录，并且重复启动不会重复写入。

## 验证

- 原作证据：tools/audit-clear-awards-v021.cjs执行CLRFLG的结算指令，六个结局的原作奖励列表依次为[0]、[1]、[2]、[3]、[4]、[3,5]。报告clear-awards-v021-source.json记录原表与指令位置；未修改原作。
- npm test通过：六条完整路线的跳章与存档恢复、结算奖励对照、旧全局记录自动修复/持久化/幂等、两页通关列表及不反向解锁；原路线/关键决策/回复/跳章/存档/UI/媒体与884帧时钟检查亦通过。
- 准确SHA包在官方Vela模拟器成功安装并完整冷启。章节选择进入原作真结局标题CG，跳章到结算，写入两项通关记录；视检两页列表，分别显示《无限远点的牵牛星》和《交差坐标的星尘》已完成。旧0.1.0存档n0:1仍可读取。证据在native-test-results-v021/。维护者随后反馈0.2.1“测试通过”，见hardware-feedback-v021.json。
- 与0.2.0逐文件对照：全部2762个common运行文件、853个正文分块、剧情图、手机数据、CG/立绘、字体、标题曲和8fps OP保持字节相同。仅修改通关记录逻辑与应用版本/签名/构建信息。包名、签名证书、R1尾部、存档外层2/状态3及30栏位保持。

## 安装封装与实机范围

沿用0.2.0低解压封装：2723个非目录文件STORE，45个文本文件DEFLATE，图片/音频/字体均直接存储。最大DEFLATE文件随编译代码增加为250478字节，未引入新媒体或额外解码开销。维护者已反馈0.2.1实机测试通过；未记录本次固件版本、耐久时长或逐字穷举范围，不能将这一反馈扩大为所有环境的保证。

更新前保留重要进度；沿用原工具覆盖更新，避免卸载清数据。蓝牙传输完成后仍需等待应用解包登记。若旧版全局记录已保存真结局，启动本版后打开EXTRA→通关记录即可查看自动补记结果。原作目录只读，旧交付保留；维护者授权将本版上传GitHub，不发邮件、不输出独立OP。
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
   if f.is_file() and not any(x in f.relative_to(R).parts for x in ['node_modules','__pycache__']) and f.suffix not in ['.pyc','.log']:
    z.write(f,f.relative_to(R).as_posix())
 for f in ['README.md','WORK_PROGRESS.md','LICENSE','package.json']:z.write(R/f,f)
 for f in reports+['install-packaging-v021.json']:z.write(R/'reports'/f,'reports/'+f)
 if hardware_path.exists():z.write(hardware_path,'reports/hardware-feedback-v021.json')
 for f in sorted((R/'native-test-results-v021').iterdir()):
  if f.suffix in ['.png','.json']:z.write(f,f.relative_to(R).as_posix())
 for f in sorted((R/'reports/before-v021').rglob('*')):
  if f.is_file():z.write(f,f.relative_to(R).as_posix())
 z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<25_000_000
files=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
 f=O/(name+ext);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v021.json').write_text(json.dumps({'version':'0.2.1','physicalDeviceTested':hardware['physicalDeviceTested'],'hardwareFeedback':hardware,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(files,ensure_ascii=False,indent=2))
