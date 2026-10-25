from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'tools/test-ui-v015.cjs').read_text('utf8')
s=s.replace("ui.sendRine(0);ui.showPhone();assert.equal(ui.phoneRows[0].meta,'有新信息');", "ui.sendRine(0);ui.showPhone();assert.match(ui.phoneRows[0].meta,/^\\d+组-\\d+条信息$/);")
start=s.index('ui._state=e.newState(longest.node');end=s.index('\nconst legacy=',start)
s=s[:start]+'''ui._state=e.newState(longest.node,true,longest.event.at);ui.present();ui.showPhone();ui.openInbox();const firstMessage=ui._state.inbox.find(x=>x.base===longest.event.base);assert.ok(firstMessage);ui.openMessage(firstMessage);ui.replyMessage();ui.sendRine(longest.index);const all=conv.conversationMessages(ui._state,ui._thread);assert.ok(all.length>=longest.count);assert.equal(new Set(all.map(x=>x.order)).size,all.length);assert.equal(ui.phoneLeftLabel,'');assert.equal(ui.phoneRightLabel,'继续剧情');assert.ok(!ui.phonePageLabel.includes('页'));assert.ok(ui.phoneHeight>322);assert.ok(ui.phoneLines.filter(x=>x.image).length>8);ui.phoneLeft();assert.equal(ui._threadPage,0);
'''+s[end:]
start=s.index('// Follow-up pages');end=s.index('// A detail',start)
s=s[:start]+'''// The complete conversation is one continuous page, unrelated conversations stay unread.
ui._state=e.newState('n0',true,591);ui.present();ui.showPhone();ui.openInbox();ui.phonePick(0);ui.phoneRight();ui.sendRine(0);
const target=ui._thread.base;assert.ok(ui._state.inbox.filter(m=>m.base===target).every(m=>ui._state.read.includes(m.key)));
const other={key:'new-other-conversation',id:2304,base:2304,date:101123,sender:1,contact:0,stamp:false,outgoing:false,order:++ui._state.mailSequence};ui._state.inbox.push(other);assert.ok(!ui._state.read.includes(other.key));ui.phoneRight();assert.equal(ui.mode,'play');assert.equal(ui.phoneLabel,'有新 RINE');ui._state.inbox=ui._state.inbox.filter(m=>m.key!==other.key);ui.refreshNotice();assert.equal(ui.phoneLabel,'手机');const saved=e.restore(e.checkpoint(ui._state));assert.ok(saved.inbox.every(m=>saved.read.includes(m.key)));
'''+s[end:]
s=s.replace('assert.ok(ui.phoneLines.filter(x=>x.image).length>8);', "assert.equal(ui.phoneLines.filter(x=>x.image).length,all.filter(m=>m.stamp).length);assert.equal(ui.phoneLines.filter(x=>x.size===19).length,all.length);")
s=s.replace('maximumMessagesPerDetailPage:8','singleContinuousConversation:true,maximumOriginalReplyMessages:longest.count')
s=s.replace('unopenedPagesAndOtherThreadsStayUnread:true','otherThreadsStayUnread:true')
s=s.replace('reports/ui-v015-tests.json','reports/ui-v016-tests.json')
needle="const reveal=load(path.join(src,'common/text-reveal.js'));"
extra='''
// Shared layers appear atomically, retain original poses, and unchanged scenes reuse rows.
ui._state=e.newState('n0',true,9);ui.present();const sceneRows=ui.sceneImages;ui.drawScene();assert.equal(ui.sceneImages,sceneRows);
const asset=load(path.join(src,'common/assets.js'));let pairKey=null;for(const node of Object.values(graph.nodes)){for(const part of node.chunks){const c=JSON.parse(fs.readFileSync(path.join(src,'common/story',part.file)));const found=c.views.flat().find(v=>asset.imagePaths(v[0]).length===2);if(found){pairKey=found[0];break;}}if(pairKey)break;}
assert.ok(pairKey);ui._state.sceneLayers=[[pairKey,0,0,200,240,1000]];ui.drawScene();assert.equal(ui.sceneImages.length,2);assert.ok(ui.sceneImages.every(r=>r.opacity===0));ui.sceneLayerLoaded(ui.sceneImages[0].key);assert.ok(ui.sceneImages.every(r=>r.opacity===0));ui.sceneLayerLoaded(ui.sceneImages[1].key);assert.ok(ui.sceneImages.every(r=>r.opacity===1));const staleKey=ui.sceneImages[1].key;ui._state.sceneLayers=[];ui.drawScene();ui.sceneLayerLoaded(staleKey);assert.equal(ui.sceneImages.length,0);
'''
s=s.replace(needle,extra+needle)
s=s.replace('Object.assign(report,{stableRowIdsObjectsAndArray:true,','Object.assign(report,{sharedLayersWaitForCompletePair:true,unchangedSceneRowsReused:true,titleMottoAndRuleUse64PixelInset:true,stableRowIdsObjectsAndArray:true,')
(R/'tools/test-ui-v016.cjs').write_text(s,encoding='utf8')
