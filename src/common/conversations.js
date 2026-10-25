// Mailbox windows group original conversation table + story date + sender.
// Metadata only: original message bodies remain in the bounded phone tables.
export function messageBase(m){return typeof m.base==='number'?m.base:m.stamp?0:Math.floor(m.id/256)*256;}
export function mailDateLabel(date){const d=Number(date)||0,m=Math.floor(d/100)%100,day=d%100;return m>=1&&m<=12&&day>=1&&day<=31?('0'+m).slice(-2)+'.'+('0'+day).slice(-2):'日期未知';}
export function threadKey(m){return messageBase(m)+':'+(m.date||0);}
export function mailboxThreads(state,sent){
 const rows=sent?state.sent:state.inbox,map={},out=[];
 for(const m of rows){const key=threadKey(m)+':'+(sent?'sent':m.sender),old=map[key];if(old){old.messages.push(m);old.latest=m;old.order=Math.max(old.order,m.order||0);}else{const t={key,base:messageBase(m),date:m.date||0,sender:m.sender,sent:!!sent,messages:[m],latest:m,order:m.order||0};map[key]=t;out.push(t);}}
 return out.sort((a,b)=>b.order-a.order);
}
export function conversationMessages(state,thread){const key=thread.base+':'+(thread.date||0);return state.inbox.concat(state.sent).filter(m=>threadKey(m)===key).sort((a,b)=>(a.order||0)-(b.order||0));}
export function threadForMessage(state,message,sent){return mailboxThreads(state,!!sent).find(t=>t.messages.some(m=>m.key===message.key))||{base:messageBase(message),date:message.date||0,sender:message.sender,sent:!!sent,messages:[message],latest:message};}

export function mailboxSummary(state){return state.inbox.some(m=>state.read.indexOf(m.key)<0)?'有新信息':mailboxThreads(state,false).length+'组-'+state.inbox.length+'条信息';}
export function canReply(state,thread){return state.replied.indexOf(thread.base)<0&&state.replyWindows.some(w=>w.base===thread.base);}
