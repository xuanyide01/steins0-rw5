export function worldlineFor(s){const n=Number(s.worldline)||1129848;return (n/1000000).toFixed(6);}
export function titleRate(p){return p.titleWorldline||'1.129848';}
export function validWorldline(v){return typeof v==='string'&&/^\d\.\d{6}$/.test(v);}
