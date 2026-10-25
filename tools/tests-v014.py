from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'tools/test-ui-v013.cjs').read_text('utf8')
start=s.index("assert.equal(replacement[0].split('_')[0],'p158');")
end=s.index('\nlet longest=',start)
s=s[:start]+"assert.equal(replacement,oldSprite);assert.equal(replacement[0].split('_')[0],'p138');"+s[end:]
extra='''
// Follow-up pages acknowledge only their incoming rows, including the sent folder.
ui._state=e.newState('n0',true,591);ui.present();ui.showPhone();ui.openInbox();ui.phonePick(0);ui.phoneRight();ui.sendRine(0);
const target=ui._thread.base,totalPages=Math.ceil(conv.conversationMessages(ui._state,ui._thread).length/8);
assert.ok(totalPages>1);assert.ok(ui._state.inbox.some(m=>m.base===target&&ui._state.read.indexOf(m.key)<0),'Unopened later page stays unread');
const other={key:'new-other-conversation',id:2304,base:2304,date:101123,sender:1,contact:0,stamp:false,outgoing:false,order:++ui._state.mailSequence};ui._state.inbox.push(other);
while(ui._threadPage<totalPages-1)ui.phoneRight();assert.ok(ui._state.inbox.filter(m=>m.base===target).every(m=>ui._state.read.includes(m.key)));
assert.ok(!ui._state.read.includes(other.key),'Unrelated unread message must not be cleared');
ui.phoneRight();assert.equal(ui.mode,'play');assert.equal(ui.phoneLabel,'有新 RINE');
ui._state.inbox=ui._state.inbox.filter(m=>m.key!==other.key);ui.refreshNotice();assert.equal(ui.phoneLabel,'手机');
const saved=e.restore(e.checkpoint(ui._state));assert.ok(saved.inbox.every(m=>saved.read.includes(m.key)));
// A detail whose pending read was abandoned is never acknowledged.
ui._state=e.newState('n0',true,591);ui.present();ui.showPhone();const pendingMessage=ui._state.inbox.find(m=>m.base===2560);ui._phoneSection='inbox';ui._phoneCache=null;delayReads=true;ui.openMessage(pendingMessage);ui.showPhone();for(const work of pending.splice(0))work();delayReads=false;assert.ok(!ui._state.read.includes(pendingMessage.key));
'''
s=s.replace('ui.onHide();assert.equal(ui._typeTimer,null);',extra+'\nui.onHide();assert.equal(ui._typeTimer,null);')
s=s.replace('daruZeroCostumeAndBaseline:true','originalScriptCostumeAndPlacement:true')
s=s.replace("reports/ui-v013-tests.json","reports/ui-v014-tests.json")
s=s.replace('Object.assign(report,{mailboxUnreadAndCounts:true,','Object.assign(report,{renderedFollowupsMarkedRead:true,unopenedPagesAndOtherThreadsStayUnread:true,staleReadNeverAcknowledged:true,readStateSurvivesRestore:true,mailboxUnreadAndCounts:true,')
(R/'tools/test-ui-v014.cjs').write_text(s,encoding='utf8')
