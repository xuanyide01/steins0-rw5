"""Export the native-tested chapter, conversation and shared-texture revision."""
from pathlib import Path
import json,re,hashlib,zipfile,shutil,copy
from rpk_signature import audit
R=Path(__file__).resolve().parents[1];O=R.parents[1]/'outputs'
name='命运石之门0-REDMIWatch5-0.1.6'
p=R/'dist/com.codex.steins0.rw5.debug.0.1.6.rpk';a=audit(p)
native=json.loads((R/'native-test-results-v016/report.json').read_text('utf8'))
assert native['result']=='passed' and native['sha256']==a['sha256']
assert a['sha256']=='eb2836fd78b9e8c2d69328ee4b017786bab9fcdaacaf49407ddf62c9c85bc875'
assert a['bytes']<=20_000_000 and a['bytes']%16==1
old=zipfile.ZipFile(O/'命运石之门0-REDMIWatch5-0.1.5-源码与检查.zip')
g=json.loads((R/'src/common/graph.txt').read_text('utf8'));baseline=json.loads(old.read('src/common/graph.txt'))
stripped=copy.deepcopy(g)
for n in stripped['nodes'].values():n.pop('chapters')
assert stripped==baseline,'Graph changed beyond chapter metadata'
cg=json.loads((R/'reports/cg-reuse-v016.json').read_text('utf8'))
shared=json.loads((R/'reports/shared-portraits-v016.json').read_text('utf8'))
proof=json.loads((R/'reports/shared-tests-v016.json').read_text('utf8'))
assert cg['allSourceRelativeMseImproved'] and shared['allSourceRelativeMseNoWorse']
assert proof['result']=='passed' and proof['compositeRGBASha256Checks']==920
allowedMissing={r['from'] for r in cg['rows']}|{r['original'] for r in shared['rows']}
unchanged=0;story=0;removed=0
for f in old.namelist():
    if not f.startswith('src/common/'):continue
    if f in ['src/common/graph.txt','src/common/engine.js','src/common/assets.js']:continue
    current=R/f
    if not current.exists():
        assert f.startswith('src/common/img/') and f[len('src/common/img/'):] in allowedMissing,f
        removed+=1;continue
    assert old.read(f)==current.read_bytes(),f
    unchanged+=1
    if f.startswith('src/common/story/'):story+=1
assert story==853
assets=(R/'src/common/assets.js').read_text('utf8')
mapping=json.loads(re.search(r'const assets=(.*);',assets).group(1))
parts=json.loads(re.search(r'const parts=(.*);',assets).group(1))
with zipfile.ZipFile(p) as z:
    for rel in set(mapping.values())|{v for seq in parts.values() for v in seq}:
        assert z.read('common/img/'+rel)==(R/'src/common/img'/rel).read_bytes(),rel
for row in cg['rows']:assert mapping[row['key']]==mapping[row['galleryKey']]
diff={'baseVersion':'0.1.5','version':'0.1.6','unchangedCommonFiles':unchanged,'unchangedStoryBlocks':story,'removedValidatedDuplicateTextures':removed,'graphOnlyAddedChaptersMetadata':True,'phoneReplyFontSaveAndMediaExact':True,'higherQualityCGsReused':176,'sharedPortraitPoses':920,'sourceRelativeMseNoWorseForEveryChangedPose':True,'compositeTargetRGBAHashesVerified':920,'saveWrapperVersion':2,'stateFormat':3,'nativeTestedSha256':a['sha256']}
for file,data in [('version-diff-v016.json',diff),('package-audit-v016.json',a)]:
    (R/'reports'/file).write_text(json.dumps(data,indent=2),encoding='utf8')
check=f'''# 《命运石之门0》REDMI Watch 5 0.1.6 检查说明

作者：xuanyide；Codex辅助完成实现及检查。2026-10-24。
本版通过官方Vela模拟器验证，尚待REDMI Watch 5实机验证。

安装包{a['bytes']:,}字节（{a['bytes']/1e6:.2f} MB），低于20,000,000字节。BIN与RPK内容相同。
SHA256：`{a['sha256']}`。

## 本次行为

“下一章”以原作章节标题为边界，不再按脚本内的场景小节停下。普通来信、普通电话沿原有可跳过路径处理；关键电话、电源操作和选项会停下等待选择，已延后的关键窗口在关闭前拦截。序章跳到第一章标题CG。六条结局路线均能使用跳章到达，11个关键决策保留；108个位置与逐帧参考遍历比较一致。

同一聊天的全部消息在一页上下滚动，取消详情分页。最长原回复38行，加上最初来信及选中回复共40条，已在原生模拟器打开、滑到底部并返回剧情。收信箱目录仍每页四组；回复时限、后续顺序、已读状态与原存档格式保留。

标题底部El Psy Kongroo和装饰线一并移至左侧64像素，长度304像素，避让四角；其余界面结构保留。

## 20 MB以内的实现

旧版23,740,993字节，新版17,008,065字节，减少6,732,928字节（约28.36%）。没有缩小现有图片尺寸或继续降低画质，没有删除剧情、回复、CG、标题动画帧或音频。

176张剧情CG与鉴赏图来自相同原始不透明资源，统一复用原有较高质量的鉴赏文件，省去重复的低质量版本。同尺寸原图对照平均MSE由48.44降为36.15，每张均改善。

920个立绘采用共享基底和透明表情差分，原32～64色自适应调色板改为共享128色。各图保持原尺寸、站位及表情；对原作同尺寸合成图的MSE逐图不增加，平均27.39降至11.63。新图是重新生成的更高色彩精度版本，并非与旧PNG逐像素相同。原作桌面图缩放到手表后的既有损失仍然存在，MSE也不等同于主观清晰度。

实际最终PNG合成结果已逐图核对920个RGBA摘要。透明演出保留原单张纹理；共享基底和差分均加载完成后成对显示，相同场景不反复重建图片节点。最多5个逻辑图层展开为7张图片，保守同屏纹理解码预算最多1,232,000字节；这是图片预算，不是手表实测总内存或长期稳定性证明。

## 验证与兼容

- 六路线、11关键决策、35回复窗口、105次原回复发送、旧存档恢复与章节跳转检查通过。
- 同页聊天、表情、未读提示、逐字/AUTO、菜单/后台暂停、双层成对加载、过期回调等界面检查通过。
- 官方Vela最终包安装及冷启动后，查看多人物差分、章节标题、关键手机拦截、40条聊天滚动、CG鉴赏及原0.1.0存档；截图已复核。本轮没有实机或数小时耐久测试。
- 对0.1.5交付源码逐字节比较，853个剧情块、手机/回复表、字体、存档和标题媒体内容保持。故事图仅新增章节索引，原节点、连接、事件、游标位置不变。原图文件的变化仅限有对照证据的共享/复用资源。
- ZIP CRC、内外签名、全文件摘要通过，相同包名与证书，存档外层2/状态3保持。

使用表盘自定义工具安装BIN，蓝牙传输完成后仍需等待解包及应用登记。重要存档请先备份；卸载或重置可能删除存档。若异常，先重启并在CONFIG关闭标题声音/动画，记录章节及操作；其他应用可正常安装而本包失败时保留现状反馈，不要反复重置。模拟器通过不保证实机永不崩溃。

保留此前交付；本版不做OP、不导出视频、不上传GitHub、不发邮件。源码包含直接构建所需资源，不需重新读取原作。画质对照与转换脚本供核对；运行共享立绘再生成脚本需要原始只读资源和Pillow/numpy等依赖。
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
    for f in ['runtime-tests.json','rine-tests-v013.json','ui-v016-tests.json','skip-tests-v016.json','shared-tests-v016.json','shared-portraits-v016.json','cg-reuse-v016.json','package-audit-v016.json','version-diff-v016.json']:z.write(R/'reports'/f,'reports/'+f)
    for f in sorted((R/'reports/before-v016').rglob('*')):
        if f.is_file() and f.suffix in ['.js','.ux','.txt']:z.write(f,f.relative_to(R).as_posix())
    for f in sorted((R/'native-test-results-v016').iterdir()):
        if f.suffix in ['.json','.png'] and f.name!='13-forty-messages-one-page.png':z.write(f,f.relative_to(R).as_posix())
    z.write(O/(name+'-检查说明.md'),'检查说明.md')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert archive.stat().st_size<=25_000_000
delivery=[]
for ext in ['.bin','.rpk','-源码与检查.zip','-检查说明.md','-使用说明.md']:
    f=O/(name+ext);delivery.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'reports/delivery-v016.json').write_text(json.dumps({'version':'0.1.6','physicalDeviceTested':False,'files':delivery},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(delivery,ensure_ascii=False,indent=2))
