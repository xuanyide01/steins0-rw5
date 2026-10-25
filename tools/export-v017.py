"""Export the tested call-name, save workflow and startup revision."""
from pathlib import Path
import json,zipfile,hashlib,shutil,copy
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.7'
p=R/'dist/com.codex.steins0.rw5.debug.0.1.7.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v017/report.json').read_text('utf8'))
assert native['result']=='passed' and native['sha256']==a['sha256']
assert a['bytes']<20_000_000 and a['bytes']%16==1
with zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.6-源码与检查.zip') as old:
    baseline=json.loads(old.read('src/common/graph.txt'));graph=json.loads((R/'src/common/graph.txt').read_text('utf8'));corrected=0
    for key,n in graph['nodes'].items():
        c=n.get('choice')
        if c and c['kind']=='call' and c['mode']==13:
            assert c['contact']==3 and c['heading']=='Amadeus 来电';b=baseline['nodes'][key]['choice'];b.update(contact=3,heading='Amadeus 来电');corrected+=1
    assert corrected==25 and graph==baseline,'Plot data changed beyond call presentation'
    unchanged=0;story=0;images=0
    for f in old.namelist():
        if not f.startswith('src/common/'):continue
        if f in ['src/common/graph.txt','src/common/engine.js','src/common/saves.js']:continue
        assert (R/f).is_file() and (R/f).read_bytes()==old.read(f),f
        unchanged+=1;story+=f.startswith('src/common/story/');images+=f.startswith('src/common/img/')
assert story==853
diff={'baseVersion':'0.1.6','version':'0.1.7','unchangedCommonFiles':unchanged,'unchangedStoryBlocks':story,'unchangedImages':images,'allMediaFontImageAndReplyBytesExact':True,'graphOnlyCorrectedAmadeusContactAndHeading':corrected,'plotEdgesEventsCursorsDatesAndChaptersUnchanged':True,'saveWrapperVersion':2,'stateFormat':3,'optionalRebuildableSlotIndexVersion':1,'nativeTestedSha256':a['sha256']}
for f,data in [('version-diff-v017.json',diff),('package-audit-v017.json',a)]:
    (R/'reports'/f).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.7 检查说明

作者：xuanyide。Codex辅助完成实现及检查。2026-10-25。
本版官方Vela模拟器检查通过，仍待REDMI Watch 5实机确认。

安装包{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），低于20 MB。BIN/RPK相同。
SHA256：`{a['sha256']}`。

## Amadeus来电名称

原作模式13使用Amadeus通话，W6613却可能仍保留上次普通RINE的联系人。图编译器原已使用Amadeus标题，后续打包器又将其改写为这个普通联系人名称，导致部分关键分支显示铃羽等名字。

修正打包器及25个节点的Amadeus通话显示资料，运行时对旧存档中缓存的错误来电名称和联系人同样纠正。电话操作列表与分支选择标题统一。剧情连接、选项接听/忽略结果及普通RINE联系人没有改变。

## 存档速度及返回

原列表读取一栏就完整restore一次，包括邮件/回复记录的深拷贝和迁移，再重绘四栏界面。新列表只保留章节、时间与短文本摘要；不保留四份完整存档。第一次浏览旧栏位会自动建立可重建摘要目录，四栏读完仅统一刷新一次；同次运行回看已缓存页无需存储读取，重启后先读一个小目录。实际选中栏位才读取完整原存档，并去除JSON解析后多余的一次深拷贝。

30个栏位、原存档外层2及状态3保持。读取始终以实际栏位内容为准，摘要不是存档替代物。摘要写入失败不使真实保存失败。保存/确认覆盖成功后直接回到同一句剧情或同一个电话分支，无需再点“返回游戏”；没有推进游标或自动代选。退出列表后的过期读取不会覆盖当前状态。

单元检查覆盖1000条历史消息的旧存档、摘要截断、旧信息迁移、首次/缓存/重启目录读取、实际读档、保存/覆盖直接返回、摘要写失败和放弃中的异步读取。模拟器也实际操作了普通剧情保存、关键Amadeus电话处保存/覆盖和重新加载。报告中的毫秒数含模拟器输入和控制器传输，不视为手表性能基准。

## 启动负荷

启动先显示标题的静态构图；设置读取完成且界面可见后，约800毫秒启动音乐，再约900毫秒启用动画。原60帧和原播放速度保留。约204KB剧情目录改为实际进入游戏、读档或章节/通关列表时才读取。读取目录/恢复存档时暂停标题媒体；进入游戏前移除动画节点。

后台、销毁会取消未开始的启动任务；快速点击START不必等待音乐和动画。模拟器已按分离的完整系统冷启检查标题及进入游戏，快速START和销毁取消另由假时钟检查覆盖。SDK本身在同次系统运行中连续am stop/start时曾在调试器inspector::WorkerImpl::doServer/uv_loop_init处断言，发生在应用脚本执行前；原生测试改为系统冷启动隔离，相关情况记入进度。本轮结果不能证明手表首次启动一定不会重启，也没有把模拟器RAM当作实机峰值或重复长期音乐耐久测试。

## 资源与验证

- 与0.1.6源码包逐字节比较，全部853个剧情块、图片、字体、标题60帧动画/音乐及手机回复表相同，没有为本版降低画质。
- 剧情图只改25个Amadeus标题/联系标识，其他节点、事件、选择连接、日期、章节和游标保持。
- 六路线、11关键决策、35回复窗口、105次回复发送、108跳章位置、逐字/AUTO/同页聊天、共享立绘及媒体单流检查通过。
- 最终包已在官方Vela模拟器安装、系统冷启及操作；截图与报告见native-test-results-v017/。ZIP CRC、内外签名及全部资源摘要通过，包名/证书保持。

蓝牙传输结束后仍需等待解包及应用登记。更新前备份重要存档；不要为了测试新版随意卸载或重置。若仍发生首次启动重启，先重启后在CONFIG关闭声音与标题动画，再记录是否仍复现及启动步骤；这些开关仍可单独控制。卸载或重置可能丢失存档。本轮没有上传GitHub、发邮件、制作OP或输出视频，旧交付保留。
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
    for f in ['runtime-tests.json','rine-tests-v013.json','skip-tests-v016.json','ui-v017-tests.json','media-tests.json','shared-tests-v016.json','call-label-v017.json','package-audit-v017.json','version-diff-v017.json']:z.write(R/'reports'/f,'reports/'+f)
    for folder in ['reports/before-v017','native-test-results-v017']:
        for f in sorted((R/folder).rglob('*')):
            if f.is_file() and f.suffix in ['.json','.txt','.js','.cjs','.ux','.png']:z.write(f,f.relative_to(R).as_posix())
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<25_000_000
files=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+ext);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v017.json').write_text(json.dumps({'version':'0.1.7','physicalDeviceTested':False,'files':files},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(files,ensure_ascii=False,indent=2))
