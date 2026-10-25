// Use the exact portrait/pose and placement chosen by the original SG0 script.
const digitalPortraits=["p114_1","p114_2","p114_3","p114_4","p114_5","p114_6","p114_7","p114_9","p114_10","p114_11","p114_12","p116_1","p116_3","p116_4","p116_5","p116_6","p116_7","p120_1","p120_2","p120_5","p120_6","p120_8","p120_9","p120_10","p120_11","p122_2","p122_3","p122_4","p122_5","p122_6","p122_7","p124_1","p126_1"];
export function presentedLayer(v){return v;}
export function amadeusImage(speaker,layers){if(String(speaker||'').indexOf('Amadeus')<0||(layers||[]).some(v=>digitalPortraits.indexOf(v[0])>=0))return '';return 'p120_1';}
