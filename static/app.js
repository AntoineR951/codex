async function runTest(){
  const company = document.getElementById('company').value.trim();
  if(!company) return;
  const created = await fetch('/runs',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({company_name:company})}).then(r=>r.json());
  await fetch(`/runs/${created.id}/execute`,{method:'POST'});
  const report = await fetch(`/runs/${created.id}/report`).then(r=>r.json());

  const rows = report.rows;
  const tb = document.querySelector('#reportTable tbody');
  tb.innerHTML='';
  let positive=0,total=0;
  rows.forEach(row=>{
    const tr=document.createElement('tr');
    const cg=row.chatgpt||''; const cl=row.claude||''; const ge=row.gemini||'';
    [row.requete,row.categorie,cg,cl,ge,row.date].forEach((val,idx)=>{const td=document.createElement('td');
      if(idx>=2&&idx<=4){const status=(val.split(' ')[0]||'');td.innerHTML=`<span class="badge ${status}">${val}</span>`;if(status==='TOP_MENTION'||status==='MENTION')positive++;total++;}
      else td.textContent=val;tr.appendChild(td);});
    tb.appendChild(tr);
  });
  const score = total ? Math.round((positive/total)*100) : 0;
  document.getElementById('score').textContent=`${score} /100`;
  document.getElementById('summary').textContent=`${rows.length} requêtes analysées, ${total} cellules chatbot.`;
}
document.getElementById('runBtn').addEventListener('click',runTest);
