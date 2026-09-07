from __future__ import annotations

import json
from typing import Any


def render_html(report: dict[str, Any]) -> str:
    payload = json.dumps(report).replace("<", "\\u003c").replace("&", "\\u0026")
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Book series order preview</title><style>
body{font:17px system-ui;background:#f5f2eb;color:#202d38;margin:auto;padding:24px;max-width:1000px}
section{background:white;border:1px solid #c4cbd1;border-radius:12px;padding:18px;margin:16px 0}
label{display:block;margin:10px 0}input{display:block;box-sizing:border-box;width:100%;padding:9px;font:inherit}
button,select{font:inherit;padding:10px;max-width:100%}button{background:#173d51;color:white;border:0;border-radius:5px}
.fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:12px}
</style><h1>Book series order preview</h1>
<p>Edit your own reading and publication orders. No canonical order is inferred.
Changes stay in this page until you download a new JSON input; your source stays unchanged.</p>
<label>Order to use on the next analysis <select id="mode"><option value="reading">Reading order</option>
<option value="publication">Publication order</option></select></label>
<div id="entries"></div><button id="save">Download edited JSON</button>
<p id="status" role="status"></p><script type="application/json" id="data">"""
        + payload
        + """</script>
<script>
const data=JSON.parse(document.getElementById('data').textContent);
document.getElementById('mode').value=data.order_mode;
for(const [i,item] of data.entries.entries()){
 const section=document.createElement('section');const heading=document.createElement('h2');
 heading.textContent=`Entry ${i+1} — analyzed order ${item.normalized_order}`;section.append(heading);
 const fields=document.createElement('div');fields.className='fields';
 for(const [key,title] of [['title','Title'],['number','Original number or special label'],['reading_order','Reading order'],['publication_order','Publication order']]){
  const label=document.createElement('label');label.textContent=title;
  const input=document.createElement('input');input.value=item[key]??'';
  input.addEventListener('input',()=>item[key]=input.value);label.append(input);fields.append(label);
 }section.append(fields);document.getElementById('entries').append(section);
}
document.getElementById('save').addEventListener('click',()=>{
 const entries=data.entries.map(item=>Object.fromEntries(Object.entries(item).filter(([k])=>!['normalized_order','display','source_index'].includes(k))));
 const output={entries,order_mode:document.getElementById('mode').value,special_labels:data.special_labels};
 const url=URL.createObjectURL(new Blob([JSON.stringify(output,null,2)],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='edited-series.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 document.getElementById('status').textContent='Downloaded new input. Run the CLI again to validate and reorder your edits.';
});</script></html>"""
    )
