from pathlib import Path
import re
R=Path(__file__).resolve().parents[1];p=R/'src/pages/index/index.ux'
s=(R/'reports/before-v012/index.ux').read_text('utf8')
s=s.replace("import {imagePath} from '../../common/assets.js';", "import {imagePath} from '../../common/assets.js';\nimport {presentedLayer,amadeusImage} from '../../common/scene-presentation.js';\nimport {mailboxThreads,conversationMessages,threadForMessage,mailDateLabel} from '../../common/conversations.js';")
s=s.replace("dateLabel:'',lines:[]", "dateLabel:'',amadeusVisible:false,amadeusSrc:'',lines:[]")
s=s.replace("phoneHeight:322,phoneRows:[]", "phoneHeight:322,phoneReplyLabel:'',phoneRows:[]")
s=s.replace('this.sceneImages=(this._state.sceneLayers||[]).map((v,i)=>', 'this.sceneImages=(this._state.sceneLayers||[]).map(presentedLayer).map((v,i)=>')
s=s.replace("this.speakerFont=textFont(this.speaker);this.dateLabel", "this.speakerFont=textFont(this.speaker);const avatar=amadeusImage(this.speaker,this._state.sceneLayers);this.amadeusVisible=!!avatar;this.amadeusSrc=avatar?imagePath(avatar):'';this.dateLabel")
s=s.replace('this._state=null;this._phoneCache=null;', 'this._state=null;this._thread=null;this._phoneItems=[];this._phonePageItems=[];this.amadeusVisible=false;this._phoneCache=null;')
old='<div class="scene" onclick="advance"><image for="{{sceneImages}}" tid="key" class="layer" src="{{$item.src}}" style="left:{{$item.left}}px;top:{{$item.top}}px;width:{{$item.width}}px;height:{{$item.height}}px;opacity:{{$item.opacity}};"></image></div>'
new=old.replace('</image></div>','</image><div if="{{amadeusVisible}}" class="amadeus-frame"><text class="amadeus-label">Amadeus</text><image class="amadeus-portrait" src="{{amadeusSrc}}"></image></div></div>')
assert old in s;s=s.replace(old,new)
old='<text for="{{phoneLines}}" tid="id" class="phone-line" style="height:{{$item.height}}px;line-height:{{$item.height}}px;font-size:{{$item.size}}px;font-family:{{$item.font}};color:{{$item.color}};">{{$item.text}}</text>'
new='<div for="{{phoneLines}}" tid="id" class="phone-part" style="height:{{$item.height}}px;"><image if="{{$item.image !== \'\'}}" class="phone-stamp" src="{{$item.image}}"></image><text if="{{$item.image === \'\'}}" class="phone-line" style="height:{{$item.height}}px;line-height:{{$item.height}}px;font-size:{{$item.size}}px;font-family:{{$item.font}};color:{{$item.color}};">{{$item.text}}</text></div>'
assert old in s;s=s.replace(old,new)
s=s.replace('<text class="phone-page-label">{{phonePageLabel}}</text>', '<text if="{{phoneReplyLabel !== \'\'}}" class="phone-reply" onclick="replyMessage">{{phoneReplyLabel}}</text><text class="phone-page-label">{{phonePageLabel}}</text>')
start=s.index('\nrefreshNotice(') if '\nrefreshNotice(' in s else s.index('\n refreshNotice(');end=s.index('\n};',start)
s=s[:start]+'\n'+(R/'tools/phone-v012.methods').read_text('utf8').strip()+'\n'+s[end:]
s=s.replace('.phone-subtitle{position:absolute;left:42px;top:82px;width:348px;', '.phone-subtitle{position:absolute;left:42px;top:82px;width:250px;')
s=s.replace('</style>', '''.phone-part{width:380px;flex-direction:column;}
.phone-stamp{width:160px;height:140px;margin-left:110px;object-fit:contain;}
.phone-reply{position:absolute;left:310px;top:80px;width:80px;height:30px;text-align:center;font-size:18px;color:#b8d7da;}
.amadeus-frame{position:absolute;left:144px;top:10px;width:144px;height:225px;background-color:#141b25;border-width:3px;border-color:#a1a2ac;flex-direction:column;}
.amadeus-label{width:138px;height:20px;font-size:13px;text-align:center;color:#aabedb;}
.amadeus-portrait{width:138px;height:199px;object-fit:contain;}
</style>''')
p.write_text(s,encoding='utf8')
