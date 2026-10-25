from pathlib import Path
import hashlib,json,shutil,zipfile
from rpk_signature import audit

R=Path(__file__).resolve().parents[1]
O=R.parents[1]/'outputs'
name='命运石之门0-REDMIWatch5-0.1.1'
p=R/'dist/com.codex.steins0.rw5.debug.0.1.1.rpk'
a=audit(p)
assert a['bytes']<=25_000_000 and a['bytes']%16==1
native=json.loads((R/'native-test-results-v011/report.json').read_text('utf8'))
assert native['result']=='passed' and native['sha256']==a['sha256']
for suffix in ['bin','rpk']:
    dest=O/(name+'.'+suffix)
    if dest.exists(): assert hashlib.sha256(dest.read_bytes()).hexdigest()==a['sha256'],'Refusing to replace a different delivery'
    shutil.copyfile(p,dest)

# Keep an explicit comparison against the preserved first delivery. Story data,
# choices, audio/animation controllers and save format must remain untouched.
old=zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.0-源码与检查.zip')
diff=[]
for entry in old.namelist():
    if not entry.startswith('src/') or entry.endswith('/'): continue
    f=R/entry
    if not f.exists() or f.read_bytes()!=old.read(entry): diff.append(entry)
added=sorted(p.relative_to(R).as_posix() for p in (R/'src').rglob('*') if p.is_file() and p.relative_to(R).as_posix() not in old.namelist())
assert not any(x.startswith(('src/common/story/','src/common/phone/','src/common/reply/')) for x in diff)
for f in ['src/common/engine.js','src/common/saves.js','src/common/graph.txt','src/common/title-music.js','src/common/title-animation.js','src/common/title-piano.wav']:
    assert (R/f).read_bytes()==old.read(f),f
comparison={'baseVersion':'0.1.0','version':'0.1.1','changedSourceFiles':diff,'addedSourceFiles':added,'storyPhoneReplyDataUnchanged':True,'engineSaveFormatMediaControllersUnchanged':True,'packageSha256':a['sha256']}
(R/'reports/version-diff-v011.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'reports/package-audit-v011.json').write_text(json.dumps(dict(a,r1LengthMod16=1),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.1 检查说明

作者：xuanyide。Codex 辅助完成资源转换、实现与检查。本版为界面与文本修订版，尚未进行本版实机测试。

- 安装包：{a['bytes']:,} 字节（{a['bytes']/1e6:.2f} MB），小于 25,000,000 字节。BIN 与 RPK 内容相同。
- SHA256：`{a['sha256']}`。
- ZIP CRC、内外签名、全部文件摘要通过；沿用同一签名证书、包名、DEFLATE / R1 封装方式。
- 与保留的 0.1.0 源码逐文件比较：剧情分块、电话/RINE 数据、场景图、运行器、存档格式、标题音频与动画控制器保持不变。手表仍读取轻量场景图，不运行原作演出计算。
- 六路线回放及途中保存恢复通过；11 个关键决策、35 个 RINE 回复窗口通过。原版文本、说话人、日期、章节和结局的桌面执行比对结果继续适用。
- 全部 853 个剧情分块、33,549 条独立图文帧的空格检查通过；实际渲染所用 3,041 个 PUA 字形无缺失/空字形。原作中文逗号与句号的 703 / 702 编号已核对并修正别名。检查规则不能证明每种标点的排版都完全复刻桌面版。
- 小/中/大字号、旧 26 号迁移、逐字/逐句/即时、九项阅读菜单、四宫格 CG、同组差分与返回原页、路线与章节第一页刷新通过自动检查。
- 官方 Vela 模拟器已成功安装最终包，读取旧 0.1.0 的 01 号测试存档至 n0 第 1 条；逐句点击不提前推进原剧情，长正文滚动、拖动不推进、AUTO、手机收信箱/已发送/联系人、原作 RINE 回复后的对话、动画表情文字占位、关键手机拦截、CG 差分与返回、路线第一页切换通过实际操作回归。
- 本次开始游戏约 {native['startMilliseconds']} ms；{len(native['skipMilliseconds'])} 次跳章约 {min(native['skipMilliseconds'])}—{max(native['skipMilliseconds'])} ms/次，包含控制器按压和稳定等待。这不是实机性能数据。
- 标题删除世界线数值；原作按键重新裁剪，去掉邻行图案，右侧空白区域不可点击。保留原作完整动态标题，未退回孤立旋转“0”。
- 音频假时钟 15 次打开/关闭，始终最多一个流，停止/销毁后无遗留计时器。本版未重做数小时音频耐久测试。保留的 0.1.0 记录验证过一次约 330 秒的模拟器真实循环边界，不能代替实机长时间测试。
- 按用户要求暂不制作 OP，没有退出应用键，不另导出视频。未上传 GitHub，未发送邮件，原游戏目录保持只读。

## 使用与取舍

CONFIG 或阅读菜单可切换字号和文字显示。逐字模式未显示完时点击补全本段；逐句模式逐句补全当前段落，显示完后再点击推进剧情；即时直接显示本段。较长正文和手机对话可上下滑动。

EXTRA → CG 鉴赏每页四组缩略图，共 106 组 / 198 张，点击画面切换同组差分；“返回列表”保留页码。所有分页写明“第几页，共几页”。手机内原动画表情以“动画表情”文本显示。

保留 30 个存档栏位与原存档键。模拟器保留 KV 的行为不代表实机卸载后仍会保留存档；有进度时优先使用工具支持的升级方式，卸载、重置前备份。

图片经过压缩。完整语音、音效、剧情背景音乐和全部演出未包含；自动路线检查不等于六条路线真人实机通关。所有新功能仍需本版 REDMI Watch 5 测试。

## 安装及异常处理

使用表盘自定义工具等兼容工具安装 BIN。蓝牙传输完成后，仍需等待手表解包登记。若未出现图标，先等几分钟并重启后检查，勿连续叠加传输；必要时备份进度后卸载测试版重装。若进入游戏或音频异常，重启后先在 CONFIG 关闭声音和标题动画，并记录章节、操作及是否可复现。

恢复出厂设置会清除数据，只在普通重启、重装无效且可以接受数据清除时考虑。官方 SDK 曾在开发者强制停止/立即启动时出现服务断言，以及覆盖测试版报 -19；最终包经设备冷启、卸载旧调试应用后安装和回归通过。上述 SDK 调试现象不能直接当作实机故障结论。

检查明细见源码包内 reports/*v011*、native-test-results-v011/report.json；完整截图保存在本机项目同名目录，源码包附主要界面样例。原版循环记录属于 0.1.0，已明确标注。
'''
(O/(name+'-检查说明.md')).write_text(check,encoding='utf8')
shutil.copyfile(R/'README.md',O/(name+'-使用说明.md'))

reports=['graph-replay.json','runtime-tests.json','runtime-resources.json','route-audit.json','source-compile.json','media.json','media-tests.json','native-title-memory.json','original-font.json','button-crops-v011.json','ui-v011-tests.json','presentation-audit-v011.json','package-audit-v011.json','version-diff-v011.json']
screens=['01-title.png','07-config-sentence.png','10-reading-menu.png','17-rine-sent.png','24-four-cg-groups.png','12-long-text-scrolled.png']
archive=O/(name+'-源码与检查.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for folder in ['src','tools']:
        for f in sorted((R/folder).rglob('*')):
            rel=f.relative_to(R)
            if not f.is_file() or any(x in rel.parts for x in ['node_modules','__pycache__']): continue
            if f.suffix in ['.pyc','.log']: continue
            z.write(f,rel.as_posix())
    for f in ['README.md','LICENSE','package.json','.gitignore','WORK_PROGRESS.md']:
        z.write(R/f,f)
    for f in reports: z.write(R/'reports'/f,'reports/'+f)
    # The migration tool can be rerun without duplicating methods.
    z.write(R/'reports/before-v011/index.ux','reports/before-v011/index.ux')
    for f in ['report.json']+screens: z.write(R/'native-test-results-v011'/f,'native-test-results-v011/'+f)
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
assert archive.stat().st_size<=25_000_000,archive.stat().st_size
files=[]
for suffix in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+suffix);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v011.json').write_text(json.dumps({'version':'0.1.1','physicalDeviceTested':False,'files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(files,ensure_ascii=False,indent=2))
