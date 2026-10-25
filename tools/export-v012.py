"""Export the exact emulator-tested 0.1.2 package, preserving older releases."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.2'
p=R/'dist/com.codex.steins0.rw5.debug.0.1.2.rpk';a=audit(p)
assert a['bytes']<=25_000_000 and a['bytes']%16==1
native=json.loads((R/'native-test-results-v012/report.json').read_text('utf8'))
assert native['result']=='passed' and native['sha256']==a['sha256']
old=zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.1-源码与检查.zip')
prior=json.loads(old.read('src/common/graph.txt'));current=json.loads((R/'src/common/graph.txt').read_text('utf8'))
assert list(prior['nodes'])==list(current['nodes'])
for key,node in prior['nodes'].items():
    new=current['nodes'][key]
    for field in ['chunks','count','choice','condition','ending','endingId','breaks']:assert node.get(field)==new.get(field),(key,field)
    assert [(e['type'],e['at']) for e in node['events']]==[(e['type'],e['at']) for e in new['events']],key
for f in old.namelist():
    if f.startswith(('src/common/story/','src/common/phone/','src/common/reply/')):assert (R/f).read_bytes()==old.read(f),f
for f in ['src/common/saves.js','src/common/title-music.js','src/common/title-animation.js']:assert (R/f).read_bytes()==old.read(f),f
history=[{'node':node,'at':e['at'],'scope':e.get('scope'),'source':e.get('source')} for node,n in current['nodes'].items() for e in n['events'] if e['type']=='rineReset']
report={'baseVersion':'0.1.1','version':'0.1.2','storyPhoneReplyTextFilesUnchanged':True,'nodeIdsChoiceEdgesCountsAndEventOrderUnchanged':True,'saveWrapperVersion':2,'stateFormat':3,'titleMediaControllersUnchanged':True,'rineResetSites':history,'routineDisplayResets':sum(x['scope']=='display' for x in history),'explicitHistoryResets':sum(x['scope']=='history' for x in history),'packageSha256':a['sha256']}
(R/'reports/version-diff-v012.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'reports/package-audit-v012.json').write_text(json.dumps(dict(a,r1LengthMod16=1),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for suffix in ['bin','rpk']:
    f=O/(name+'.'+suffix)
    if f.exists():assert hashlib.sha256(f.read_bytes()).hexdigest()==a['sha256'],'Different delivery already exists'
    shutil.copyfile(p,f)
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.2 检查说明

作者：xuanyide。Codex 辅助完成转换、实现和检查。本版尚未进行实机测试。

安装包 {a['bytes']:,} 字节（{a['bytes']/1e6:.2f} MB），小于 25,000,000 字节；BIN/RPK 内容相同。
SHA256：`{a['sha256']}`。
ZIP CRC、内外签名、全部文件摘要通过，沿用相同包名、签名证书与 DEFLATE / R1 封装。

## 本次修改

1. 修复字体本身的左边距。3,652 个字形原先被写为零边距，现在与实际轮廓起点一致；保持原作字形、PUA 编号和前进字宽不变。文字串清理继续去除中文与标点附近布局空格，并保留英文词间空格。模拟器已查看“我眯起眼睛”等实际样例。
2. RINE 收信箱仍用“动画表情”作摘要；进入对话改为对应原作表情图片的静态帧。回复后的收发记录也保留图片。同一原作会话表、日期与发信人的多条消息合并为一个入口，标注消息数量。
3. 对话详情按时间顺序显示，最多每页 8 条，通过底部“较早消息 / 较新消息”翻阅；有回复窗口时，右上角显示“回复”。浏览历史不重新开放已过期的回复。收信箱打开后仍标记当前收到消息已读。
4. 修正历史丢失：macrosys2:612 的普通日期/章节显示重置保留既有收发记录；原作世界线变化动画的 macrosys2:311 和显式清空的 macrosys2:444 清除旧记录。分类来自调用上下文的脚本分析，尚未逐条与运行中的桌面原作手机界面做人工对照；如发现具体历史记录存在差异，应提供章节和对话位置继续核对。
5. Amadeus 发言且当前画面没有原作数字红莉栖图层时，补充手机屏幕式立绘，来源为《命运石之门0》chara.mpk 的 CRS_JMD。当前用静态站姿，不包含原作 3D 手机、唇形或完整表情动画，未改剧情文字或选项。
6. 素材来源核查确认立绘均来自《0》的资源包；包内包含旧造型。按要求把桥田至 DAR_AMA / DAR_AMB / DAR_ASA 映射到《0》的冬装 DAR_DMC / DAR_DSC，保留相同表情编号、原身体下沿与站位。CG 图片本身未替换人物。

保留 0.1.1 的小/中/大字号、逐字/逐句/即时、四组 CG/页、差分、原作风格 UI、30 存档、三档 AUTO、关键手机节点拦截和原作动态标题。仍不制作 OP，不加退出应用键，不另导出视频。没有上传 GitHub 或发邮件。

## 验证

- 六路线的原脚本桌面执行器与场景图回放，文本、人物、日期、章节与结局摘要再次一致；手表运行器六路线、途中存读档、11 个关键节点和 35 个 RINE 回复窗口通过。
- 与 0.1.1 逐项比较：853 个剧情分块、电话文字和回复数据不变；节点标识、选项连接、分块顺序、事件类型和发生位置不变，只为事件补充日期、会话表和重置范围。存档外层版本 2 / 状态格式 3 保持，旧存档新增消息元数据可迁移。
- UI 回归覆盖合并 2 条消息、图片表情、跨日期旧对话、原作最长 38 条回复的分页、重复表情不丢失、旧元数据迁移、Amadeus 立绘、桥田至替换与身体下沿保持、三档显示、CG 与关键操作。
- 最终包经官方 Vela 模拟器成功安装，实际操作并截图核对正文、桥田至冬装、消息数量、收发与回复、原作表情、日期推进后的旧消息和 Amadeus 立绘。详情见 native-test-results-v012/report.json；正文与手机滚动、存读档等 0.1.1 记录仍保留并标明版本。
- 标题音频、动画控制器未改；音频假时钟开关 15 次仍通过，始终最多一个流。没有在本版重复数小时或真机耐久测试，不能据此保证设备永不崩溃。

旧存档能保留其中实际存在的消息，但旧版已经丢失、未写入存档的历史与回复无法恢复。不要为了补历史而覆盖必要进度；新开游戏会完整记录本版之后经过的对话。

## 安装和异常恢复

用表盘自定义工具等兼容工具安装 BIN。蓝牙传输完成后继续等待手表解包和登记。有进度时优先使用工具支持的升级方式；卸载或重置可能删除存档，先备份。

若传输完成后无图标，先等几分钟、重启检查，勿连续叠加传输。仍失败时备份后卸载测试版重装。如进入游戏或声音异常，重启后在 CONFIG 关闭声音和标题动画，并记录章节与操作。恢复出厂设置会清除数据，仅在一般重启/重装无效且接受清除时考虑。

本版尚待 REDMI Watch 5 实机验证。源码包含主要截图和检查报告，完整本机截图在项目 native-test-results-v012/。
'''
(O/(name+'-检查说明.md')).write_text(check,encoding='utf8');shutil.copyfile(R/'README.md',O/(name+'-使用说明.md'))
files=['README.md','LICENSE','package.json','.gitignore','WORK_PROGRESS.md']
reports=['graph-replay.json','runtime-tests.json','runtime-resources.json','media.json','media-tests.json','native-title-memory.json','ui-v012-tests.json','presentation-v012.json','package-audit-v012.json','version-diff-v012.json']
screens=['03-font-open-eyes.png','04-daru-zero-costume.png','07-grouped-inbox-before-reply.png','15-original-sticker.png','16-past-messages-next-date.png','18-amadeus-phone-portrait.png']
archive=O/(name+'-源码与检查.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for folder in ['src','tools']:
        for f in sorted((R/folder).rglob('*')):
            rel=f.relative_to(R)
            if not f.is_file() or any(x in rel.parts for x in ['node_modules','__pycache__']):continue
            if f.suffix in ['.pyc','.log']:continue
            z.write(f,rel.as_posix())
    for f in files:z.write(R/f,f)
    for f in reports:z.write(R/'reports'/f,'reports/'+f)
    for f in ['report.json']+screens:z.write(R/'native-test-results-v012'/f,'native-test-results-v012/'+f)
    for version in ['v011','v012']:z.write(R/f'reports/before-{version}/index.ux',f'reports/before-{version}/index.ux')
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<=25_000_000,archive.stat().st_size
delivery=[]
for suffix in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+suffix);delivery.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v012.json').write_text(json.dumps({'version':'0.1.2','physicalDeviceTested':False,'files':delivery},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(delivery,ensure_ascii=False,indent=2))
