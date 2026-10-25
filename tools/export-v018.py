"""Export the native-tested opening revision; no standalone video/audio export."""
from pathlib import Path
import json,zipfile,hashlib,shutil
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.8'
p=R/'dist/com.codex.steins0.rw5.debug.0.1.8.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v018/report.json').read_text('utf8'));media=json.loads((R/'reports/opening-v018-source.json').read_text('utf8'))
assert native['result']=='passed' and native['sha256']==a['sha256']
assert a['bytes']<25_000_000 and a['bytes']%16==1
assert media['allAtlasesDecoded'] and media['frameSize']==[256,144]
with zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.7-源码与检查.zip') as old:
    unchanged=0;story=0
    for f in old.namelist():
        if not f.startswith('src/common/'):continue
        if f in ['src/common/engine.js','src/common/title-music.js','src/common/media.txt']:continue
        assert (R/f).is_file() and (R/f).read_bytes()==old.read(f),f
        unchanged+=1;story+=f.startswith('src/common/story/')
assert story==853
with zipfile.ZipFile(p) as z:
    for row in media['atlases']:assert hashlib.sha256(z.read('common/opening/'+row['file'])).hexdigest()==row['sha256']
    assert hashlib.sha256(z.read('common/opening/op.mp3')).hexdigest()==media['audioSHA256']
diff={'baseVersion':'0.1.7','version':'0.1.8','unchangedCommonFiles':unchanged,'unchangedStoryBlocks':story,'graphAndAllPlotChoicesDatesAndEventsExact':True,'oldImagesFontsTitleFramesMusicAndPhoneReplyResourcesExact':True,'openingSourceCue':{'node':'n0','cursor':934},'optionalOpeningDoneSaveField':True,'legacyPostPrologueSaveSkipsReplay':True,'saveWrapperVersion':2,'stateFormat':3,'nativeTestedSha256':a['sha256']}
for f,data in [('version-diff-v018.json',diff),('package-audit-v018.json',a)]:
    (R/'reports'/f).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.8 检查说明

作者：xuanyide；Codex辅助完成资源转换、实现与检查。2026-10-25。
本版官方Vela模拟器验证通过，仍待REDMI Watch 5实机确认。

安装包{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），低于最新25 MB限制。BIN/RPK相同。
SHA256：`{a['sha256']}`。

## OP内容与接续

源文件为用户Steam原作USRDIR/movie/1280x720/OP.bk2（95,507,660字节，摘要{media['sourceSHA256']}），3311帧、约29.9701fps、110.4768秒。只读复制到工作区转换，不修改原游戏。原转换审计图在n0游标934记录序章OP标记，第一章也从该位置开始；本版在显示该处文本/标题前播放OP。

序章逐句阅读或“下一章”均可到达OP，跳章会停在OP。整屏黑底，384×216画面居中（左24、顶149），没有文本框/按钮覆盖；点击任意位置可跳过。自然结束或点击后先第一章原标题CG，再原正文，同一游标不被略过。EXTRA新增OP MOVIE，独立观看结束或跳过后返回EXTRA，不修改剧情或序章播放标记。

## 参照前作的技术

沿用《命运石之门》0.3.0实机通过版本的12fps、小图集和单图片方案，没有恢复负担更重的24fps双图片交替。按用户放宽至25 MB，OP以256×144、JPEG质量35生成1326帧，每8帧组成1024×288小图集，共166张，图片合计4,580,429字节。显示图集为1536×432，用384×216视口逐格裁切；无需在手表解码Bink/MP4。一个时钟根据前台累计时间定位画面，加载慢时不会把整段视频拖长，不预载整部影片。

音轨为原OP声音转MP3 22050Hz单声道48kbps，共663,527字节。CONFIG游戏音量统一控制标题音乐及OP。共用一个原生音频播放器，进入时先释放标题曲；首张图片完成才开OP声音与画面时钟。后台暂停、恢复按暂停位置续播；跳过/结束/销毁清理时钟和播放器。图片失败或首帧超时安全略过，避免死档。标题音乐原PCM保护尾、提前停止和延迟重播机制保留。

单张图集RGBA预算1,179,648字节，显示尺寸上界2,654,208字节，仅是纹理预算，不是实机总内存。高于最初19.53 MB候选的192×108/q18，但仍使用相同单图片/12fps框架。没有测得实机帧率，也不保证永不重启；若播放不稳，可先关闭CONFIG声音并点击跳过。

## 验证与兼容

- 最终包通过原生完整有声序章OP、第一章标题CG/正文接续、EXTRA点击跳过、完整静音EXTRA、重复三次打开/跳过，以及原0.1.0存档n0:1加载。对应最终摘要及截图见native-test-results-v018/。
- 假时钟覆盖OP首帧音画门控、后台暂停/续播、开关声音、序章跳章、章节直达、旧档迁移、EXTRA不改进度、超时及销毁清理。原六路线、11关键决策、35回复窗口、105次回复发送、108跳章及存档/UI/媒体检查保持通过。
- 与0.1.7交付源码比较：853剧情块、剧情图/分支/日期、全部原CG立绘、字库、标题60帧/音乐、手机回复及存档栏位资源逐字节保持。仅加入OP资源及播放逻辑，可选openingDone字段对旧第一章之后存档按已播放迁移；存档外层2、状态3及30个栏位key不变。
- 全部166张图集逐张解码/尺寸/摘要及包内资源摘要核对，ZIP CRC、内外签名通过，包名和证书保持。模拟器内存和播放耗时仅为该环境观察，不能代替手表听觉、流畅度和耐久验证。

通过表盘自定义工具安装，蓝牙传输完成后继续等待解包及登记。更新前备份重要进度；不要为了测试随意卸载或重置实机。旧交付保留，不新输出独立OP视频/音轨，不发邮件、不上传GitHub。
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
    for f in ['runtime-tests.json','rine-tests-v013.json','skip-tests-v016.json','ui-v018-tests.json','media-tests.json','opening-v018-source.json','opening-pixels-v018.json','package-audit-v018.json','version-diff-v018.json']:z.write(R/'reports'/f,'reports/'+f)
    for folder in ['reports/before-v018','native-test-results-v018']:
        for f in sorted((R/folder).rglob('*')):
            if f.is_file() and f.suffix in ['.json','.txt','.js','.cjs','.ux','.png']:z.write(f,f.relative_to(R).as_posix())
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<25_000_000
files=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+ext);files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v018.json').write_text(json.dumps({'version':'0.1.8','physicalDeviceTested':False,'files':files},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(files,ensure_ascii=False,indent=2))
