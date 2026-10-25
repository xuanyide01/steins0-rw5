"""Deliver the native-tested text-reveal/icon revision without touching older releases."""
from pathlib import Path
import json,hashlib,zipfile,shutil
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.5';p=R/'dist/com.codex.steins0.rw5.debug.0.1.5.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v015/report.json').read_text('utf8'));assert native['result']=='passed' and native['sha256']==a['sha256'];assert a['bytes']<=25_000_000 and a['bytes']%16==1
old=zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.4-源码与检查.zip');unchanged=0
for f in old.namelist():
    if f.startswith('src/common/') and f!='src/common/logo.png':assert old.read(f)==(R/f).read_bytes(),f;unchanged+=1
with zipfile.ZipFile(p) as z:assert z.read('common/logo.png')==(R/'src/common/logo.png').read_bytes()
diff={'baseVersion':'0.1.4','version':'0.1.5','unchangedExistingCommonResourcesExceptLogo':unchanged,'storyPhoneReplyGraphFontSaveMediaAndImageResourcesExact':True,'newTextRevealHelper':'text-reveal.js','singleGlyphTickMilliseconds':30,'rowsCreatedOncePerParagraph':True,'iconChanged':True,'saveWrapperVersion':2,'stateFormat':3,'nativeTestedSha256':a['sha256']}
for file,data in [('version-diff-v015.json',diff),('package-audit-v015.json',a)]:
    (R/'reports'/file).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.5 检查说明

作者：xuanyide；Codex辅助完成实现、资料检索、图标处理和检查。日期：2026-10-24。
本版尚待REDMI Watch 5实机验证。

安装包 {a['bytes']:,} 字节（{a['bytes']/1e6:.2f} MB），小于25 MB。BIN/RPK相同。
SHA256：`{a['sha256']}`。

## 逐字显示

原实现每60毫秒按墙钟累计字符数（约两个字）更新，并用新标识重建整组行节点，容易出现成组跳字、界面对象分配和反复排版。参考《ATRI》《eden》等移植的逐字计时方式，改为单次30毫秒计时、每回调推进一个字符，并为每段建立稳定的行数组/对象/标识，逐字时只改行内文字。换行直接进入下一行，Unicode代理对不从中切开。

文字行高度固定34像素，多行预留完整空间，正文仍可滚动。手动点击先补全、逐句/即时显示、AUTO字完后等待、菜单/手机/后台暂停、旧回调代际失效均保留。标题音频/动画控制器和剧情运行器未变。

单元检查证明30毫秒单步、行对象/数组/标识不随逐字重建，后台/菜单后旧回调不再修改文字。官方Vela模拟器已查看单行、多行逐字过程与完成结果、AUTO推进和菜单暂停、逐句/即时以及原0.1.0存档n0游标1；截图见native-test-results-v015/。这不是实机帧率或长期性能测量，手表上的具体观感仍待本版实测。

## 图标

用户图片对应《Amadeus》唱片插画，原插画署名huke。官方资料：https://music.ani-tone.com/release/FVCG-1354/ 。检索到同幅1920×1080壁纸：https://www.goodfon.ru/other-anime/wallpaper-download-1920x1080-kurisu-makise-makise-kurisu.html 。
原壁纸左下有标题，裁剪人物所在的[1110,0,1830,720]区域排除了文字，再缩成192×192透明圆形图标；没有重绘人物。原图、裁剪记录和预览见reports/icon-v015/及reports/icon-v015.json。标题界面继续使用原作动态标题。

## 验证及兼容

- 当前UI检查覆盖逐字/逐句/即时、稳定行标识、过期回调、菜单/后台暂停、RINE已读、旧存档和原有界面功能。
- 六路线、11关键节点、35RINE窗口、105次原选项发送检查通过。
- 与0.1.4交付源码逐字节比较：旧common资源除logo外全相同，涵盖剧情/手机/回复表、故事图、字体、存档、标题媒体、立绘/CG文件；新增轻量显示辅助模块。没有继续降低图片画质。存档外层2/状态3保持。
- 最终包经官方Vela安装与冷启动，原生操作和截图已核对，ZIP CRC、内外签名及摘要通过。没有重复本版真机长时间音乐或内存耐久测试。

用兼容工具安装BIN；蓝牙传输后继续等待解包和登记。有重要进度先备份，卸载和重置可能删除存档。如运行异常，重启后在CONFIG关闭声音/标题动画并记录章节与操作。模拟器通过不能替代本版实机测试。

保留旧版交付文件；不制作OP、不导出视频、不上传GitHub、不发邮件。
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
    for f in ['runtime-tests.json','rine-tests-v013.json','ui-v015-tests.json','icon-v015.json','package-audit-v015.json','version-diff-v015.json']:z.write(R/'reports'/f,'reports/'+f)
    z.write(R/'reports/icon-v015/amadeus-wallpaper-1920.jpg','reports/icon-v015/amadeus-wallpaper-1920.jpg')
    z.write(R/'reports/before-v015/src/pages/index/index.ux','reports/before-v015/src/pages/index/index.ux')
    for f in ['report.json','02-typing-0.png','03-typing-completed.png','09-multiline-complete.png']:z.write(R/'native-test-results-v015'/f,'native-test-results-v015/'+f)
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<=25_000_000,archive.stat().st_size
delivery=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+ext);delivery.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v015.json').write_text(json.dumps({'version':'0.1.5','physicalDeviceTested':False,'files':delivery},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(delivery,ensure_ascii=False,indent=2))
