"""Deliver only the exact native-tested build; preserve earlier files."""
from pathlib import Path
import json,hashlib,zipfile,shutil,re
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.3';p=R/'dist/com.codex.steins0.rw5.debug.0.1.3.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v013/report.json').read_text('utf8'));assert native['result']=='passed' and native['sha256']==a['sha256'];assert a['bytes']<=25_000_000 and a['bytes']%16==1
old=zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.2-源码与检查.zip');g=json.loads((R/'src/common/graph.txt').read_text('utf8'));prior=json.loads(old.read('src/common/graph.txt'))
for node,n in prior['nodes'].items():
    now=g['nodes'][node]
    for f in ['chunks','count','choice','condition','ending','endingId','breaks']:assert n.get(f)==now.get(f),(node,f)
    assert [(e['type'],e['at']) for e in n['events']]==[(e['type'],e['at']) for e in now['events']]
for f in old.namelist():
    if f.startswith(('src/common/story/','src/common/phone/','src/common/reply/')):assert old.read(f)==(R/f).read_bytes(),f
for f in ['src/common/saves.js','src/common/title-music.js','src/common/title-animation.js']:assert old.read(f)==(R/f).read_bytes()
mapping=json.loads(re.search(r'const assets=(.*);',(R/'src/common/assets.js').read_text('utf8')).group(1));keys=set(['p120_1','p158_1','p158_4','p166_1'])
for n in g['nodes'].values():
    for part in n['chunks']:
        for view in json.loads((R/'src/common/story'/part['file']).read_text('utf8'))['views']:
            for layer in view:keys.add(layer[0])
for row in json.loads((R/'src/common/gallery.txt').read_text('utf8')):keys.update(row['images'])
for key in keys:assert key in mapping and (R/'src/common/img'/mapping[key]).is_file(),key
diff={'baseVersion':'0.1.2','version':'0.1.3','storyAndPhoneTextAndReplyTablesUnchanged':True,'narrativeGraphEdgesAndEventPositionsUnchanged':True,'saveWrapperVersion':2,'stateFormat':3,'titleMediaUnchanged':True,'nativeTestedSha256':a['sha256']}
(R/'reports/version-diff-v013.json').write_text(json.dumps(diff,indent=2),encoding='utf8');(R/'reports/package-audit-v013.json').write_text(json.dumps(a,indent=2),encoding='utf8')
quality=json.loads((R/'reports/portrait-quality-v013.json').read_text('utf8'));improvement=100*(1-quality['newMeanMse']/quality['oldMeanMse'])
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.3 检查说明

作者：xuanyide；资源转换、实现与检查由 Codex 辅助完成。日期：2026-10-24。
本版尚待 REDMI Watch 5 实机验证。

安装包 {a['bytes']:,} 字节（{a['bytes']/1e6:.2f} MB），小于 25,000,000 字节。
SHA256：`{a['sha256']}`。BIN 和 RPK 相同，沿用原包名、签名和兼容封装。

## 本次修复

- 立绘原先经过两次调色板减色。现直接从《命运石之门0》原始 chara.mpk 重建，在可见像素上分配颜色，按图片自适应使用调色板；{quality['updatedPortraits']} 张转换立绘更新。去除 {quality['prunedUnreferencedFiles']} 张未被剧情、鉴赏和补充立绘引用的转换图片，腾出约 {quality['prunedBytes']/1e6:.2f} MB。原作文件未改。
- 相对“原始立绘合成后以相同尺寸缩小”的对照，全部保留立绘的平均像素均方误差减少约 {improvement:.1f}%。这只是离线同尺寸压缩误差指标，不代表主观清晰度提高相同比例。图片解码尺寸、画面站位和图层数量保持，避免通过扩大纹理增加内存开销；仍有小屏缩放和调色板损失。
- 手机首页收信箱有未查看信息时显示“有新信息”，全部查看后显示“X组-Y条信息”；打开收信箱仍统一标记当前信息为已读，之后新到的信息重新提示。
- 可回复对话在收信箱标注“可回复”；详情保留右上入口，并增加底部“回复”按键。原作有选项时显示三个对应选项；表情回复显示实际原作图片，可滑动查看。没有原作回复选项和已经过期的对话分别提示，浏览旧信息不重新开放过期选项。
- 修复发送记录漏掉玩家选中的第一条文字/表情：先记录该条发送，再按原顺序记录后续收发。回复沿用原会话日期，不因当前界面日期尚未加载而分散到未知日期。
- 逐项核查 16 个可达原作回复表、48 个选项及其后续序列；35 个回复截止位置保留。按原脚本的已查看/未查看分支补充截止后的消息；回复后不再追加未选择的默认分支。相关审计依据为原 SC3 指令和表，不声称已人工逐一操作桌面原作手机界面。

普通 RINE 仍可由“下一章”略过，因此跳过回复时机后看到历史消息而不能回复属于原作窗口规则。可从回复窗口内的存档继续，或重新经过该段；旧版未记录的已选回复与历史不能凭空恢复。

## 验证

- 手表运行器六条结局路径、途中存读档、11 个关键手机节点与35个RINE窗口通过。
- 对全部可达窗口执行105次选项发送测试；核对首条发送、原后续顺序、表情、重复消息、保存恢复、默认分支去重；35个截止位置分别验证已查看和未查看的后续分支。
- UI 回归：底部回复、列表可回复提示、过期原因、未读及数量、表情选项、正文显示、CG、旧元数据与异步过期保护。
- 最终包在官方 Vela 模拟器完成安装与操作检查，实际截图核对立绘、未读/数量、底部回复、原作选项、首条发送和表情回复；读取原0.1.0存档 n0 游标1成功。见 native-test-results-v013/report.json。
- ZIP CRC、内外签名及所有文件摘要通过。对比0.1.2：剧情文字、手机文本、回复数据文件、故事连接和事件位置不变，增加消息分支元数据并修复运行时记录/界面。存档格式保持外层2、状态3。
- 标题媒体控制器不变，单流音频/计时器测试仍通过；本次未重复数小时或实机耐久测试。

## 安装与异常处理

用兼容工具安装BIN，蓝牙传输后继续等待解包和登记。有进度时先备份，再按工具支持的方式升级；卸载或恢复出厂设置可能清除存档。
若无图标，等待后重启检查，避免连续传输。若运行异常，重启后先在CONFIG关闭声音及标题动画，并记录章节、操作及复现步骤。模拟器检查通过不能替代本版实机测试。

保留旧版交付包；本版不制作OP，不另导出视频，不上传GitHub，不发邮件。
'''
(O/(name+'-检查说明.md')).write_text(check,encoding='utf8')
for ext in ['bin','rpk']:
    target=O/(name+'.'+ext)
    if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==a['sha256']
    shutil.copyfile(p,target)
shutil.copyfile(R/'README.md',O/(name+'-使用说明.md'))
archive=O/(name+'-源码与检查.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for folder in ['src','tools']:
        for f in sorted((R/folder).rglob('*')):
            if f.is_file() and not any(x in f.relative_to(R).parts for x in ['node_modules','__pycache__']) and f.suffix not in ['.pyc','.log']:z.write(f,f.relative_to(R).as_posix())
    for f in ['README.md','LICENSE','package.json','WORK_PROGRESS.md']:z.write(R/f,f)
    for f in ['runtime-tests.json','rine-audit-v013.json','rine-tests-v013.json','ui-v013-tests.json','package-audit-v013.json','version-diff-v013.json','media-tests.json','portrait-quality-v013.json']:z.write(R/'reports'/f,'reports/'+f)
    for f in ['index.ux','engine.js','conversations.js','graph.txt','assets.js']:z.write(R/'reports/before-v013'/f,'reports/before-v013/'+f)
    z.write(R/'native-test-results-v013/report.json','native-test-results-v013/report.json');z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<=25_000_000,archive.stat().st_size
delivery=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+ext);delivery.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v013.json').write_text(json.dumps({'version':'0.1.3','physicalDeviceTested':False,'files':delivery},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(delivery,ensure_ascii=False,indent=2))
