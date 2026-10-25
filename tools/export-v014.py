"""Export the exact native-tested version, auditing image pixels against v0.1.3."""
from pathlib import Path
import io,json,hashlib,zipfile,shutil
from PIL import Image
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs';name='命运石之门0-REDMIWatch5-0.1.4';p=R/'dist/com.codex.steins0.rw5.debug.0.1.4.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v014/report.json').read_text('utf8'));assert native['result']=='passed' and native['sha256']==a['sha256'];assert a['bytes']<=25_000_000 and a['bytes']%16==1
old=zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.3-源码与检查.zip');pngs=0;jpegs=0
for f in old.namelist():
    if f.startswith(('src/common/story/','src/common/phone/','src/common/reply/')) or f in ['src/common/graph.txt','src/common/saves.js','src/common/title-music.js','src/common/title-animation.js','src/common/sg-original.ttf','src/common/assets.js']:
        assert old.read(f)==(R/f).read_bytes(),f
    if f.startswith('src/') and f.endswith('.png'):
        before=Image.open(io.BytesIO(old.read(f)));after=Image.open(R/f)
        assert before.size==after.size and before.getpalette()==after.getpalette() and before.info.get('transparency')==after.info.get('transparency'),f
        assert before.convert('RGBA').tobytes()==after.convert('RGBA').tobytes(),f;pngs+=1
    elif f.startswith('src/') and f.endswith(('.jpg','.jpeg')):assert old.read(f)==(R/f).read_bytes(),f;jpegs+=1
diff={'baseVersion':'0.1.3','version':'0.1.4','storyPhoneAndReplyDataAndGraphExact':True,'assetsMapAndFontAndSaveAndMediaControllersExact':True,'pngPixelsPaletteAlphaAndDimensionsExact':True,'pngsChecked':pngs,'unchangedJpegs':jpegs,'originalScriptPortraitPlacement':True,'saveWrapperVersion':2,'stateFormat':3,'nativeTestedSha256':a['sha256']}
for file,data in [('version-diff-v014.json',diff),('package-audit-v014.json',a)]:
    (R/'reports'/file).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.4 检查说明

作者：xuanyide；Codex辅助完成实现、资源处理与检查。日期：2026-10-24。
本版尚待REDMI Watch 5实机验证。

安装包 {a['bytes']:,} 字节（{a['bytes']/1e6:.2f} MB），小于25 MB。BIN/RPK相同。
SHA256：`{a['sha256']}`。

## 修改

1. 回复后的新消息原先只在打开收信箱时标记已读，聊天页显示未更新已读集合。现对成功呈现的聊天页逐条标记来信已读，覆盖从“已发送”进入的对话；翻完各页再“继续剧情”后，不再错误显示这些已读信息。未打开的后页、其他新对话仍保留提示，过期异步读取不误标。存读档保持已读状态。此前“打开收信箱统一标记现有消息已读”的行为继续保留。
2. 取消桥田至的强制冬装映射，直接采用原作脚本指定的立绘编号、表情、位置与尺寸；原作调用前作造型的场景遵循原作。Amadeus补充手机式静态立绘继续使用《0》的原资源。
3. 参考《ATRI》的PNG扫描行过滤/DEFLATE搜索与《anemoi》的构建阶段Zopfli压缩，无损重编码1146张PNG。图片文件从12,690,442字节降到11,649,697字节，共节省1,040,745字节；最终包相比0.1.3节省1,038,384字节（约4.19%）。没有继续减色、缩图或降低JPEG质量。逐图对照0.1.3交付源码，PNG的尺寸、像素、调色板、透明度完全一致，JPEG字节不变。

压缩减少安装包和文件存储占用。运行时仍解码普通PNG，图片尺寸和图层数保持，因此不声称同等减少纹理解码RAM。没有改为需要额外缓存的图集或增加手表端解压逻辑。

## 验证

- UI回归覆盖回复后首/末页已读、未打开后页和其他对话仍未读、返回剧情恢复“手机”、过期异步读取不误标、存档恢复，以及原有文字/CG/回复功能。
- 原作立绘编号与站位不再经过人工换装映射；原生模拟器核对桥田至的原作造型。
- 六路线、11个关键节点、35个RINE回复窗口与105次原作选项发送回归通过。故事图、853个剧情分块、手机文字和回复表与0.1.3完全一致。
- 最终包在官方Vela模拟器安装成功，实际回复、翻到后续消息最后一页、继续剧情，确认手机按钮恢复正常、收信箱显示数量；原生解码立绘、CG缩略图/大图正常，读取原0.1.0存档n0游标1成功。见native-test-results-v014/report.json及截图。
- ZIP CRC、内外签名、全部摘要通过，沿用原包名、证书与兼容封装。存档外层2/状态3、原字体、标题音频/动画控制器不变。没有重复本版实机长时间耐久测试。

## 使用

用兼容工具安装BIN，蓝牙传输后继续等待解包与登记。有重要进度请先备份；卸载和恢复出厂设置可能清除存档。若安装后无图标，先等待并重启检查，避免连续重复传输。运行异常时重启后先在CONFIG关闭音量/标题动画，并记录章节、操作与复现位置。

保留此前版本文件；不制作OP、不另导出视频、不上传GitHub、不发邮件。模拟器通过不能替代本版实机测试。
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
    for f in ['runtime-tests.json','rine-audit-v013.json','rine-tests-v013.json','ui-v014-tests.json','lossless-png-v014.json','package-audit-v014.json','version-diff-v014.json']:z.write(R/'reports'/f,'reports/'+f)
    for f in ['src/common/engine.js','src/common/scene-presentation.js','src/pages/index/index.ux']:z.write(R/'reports/before-v014'/f,'reports/before-v014/'+f)
    for f in ['report.json','02-original-daru-costume.png','05-return-to-story-no-false-unread.png','06-inbox-counts-after-reading.png']:z.write(R/'native-test-results-v014'/f,'native-test-results-v014/'+f)
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<=25_000_000
delivery=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+ext);delivery.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v014.json').write_text(json.dumps({'version':'0.1.4','physicalDeviceTested':False,'files':delivery},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(delivery,ensure_ascii=False,indent=2))
