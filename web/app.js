const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function addMessage(role,html){
  const row=document.createElement('div');
  row.className='message '+role;
  row.innerHTML=role==='assistant'?'<span class="avatar">MC</span><div class="bubble">'+html+'</div>':'<div class="bubble">'+html+'</div>';
  $('messages').appendChild(row);
  $('messages').scrollTop=$('messages').scrollHeight;
}
function formatReply(text){
  return '<p>'+esc(text).replace(/\n\n/g,'</p><p>').replace(/\n- /g,'<br>• ')+'</p>';
}
function renderMedication(m){
  if(!m){
    $('med-title').textContent='No medicine loaded';
    $('med-content').innerHTML='<p class="muted">Ask about a generic or brand name to query the public drug-label dataset.</p>';
    return;
  }
  $('med-title').textContent=m.generic_names?.[0]||m.brand_names?.[0]||m.query;
  const section=(title,items)=>items?.length?'<div class="med-section"><b>'+title+'</b><p>'+esc(items[0])+'</p></div>':'';
  $('med-content').innerHTML=
    '<div class="name-row"><strong>'+esc((m.generic_names||[]).join(', ')||'—')+'</strong><small>'+esc((m.brand_names||[]).slice(0,3).join(', ')||'No brand names in record')+'</small></div>'+
    section('Labelled use',m.indications)+section('Warnings',m.warnings)+section('Contraindications',m.contraindications)+section('Interactions',m.interactions)+section('Adverse reactions',m.adverse_reactions)+
    '<small class="dataset">Dataset: '+esc(m.dataset)+'</small>';
}
function renderSources(items){
  $('sources').innerHTML=items?.length?items.map(s=>'<a class="source-link" href="'+esc(s.url)+'" target="_blank" rel="noopener noreferrer"><b>'+esc(s.title)+'</b><small>'+esc(s.kind.replace('_',' '))+' ↗</small></a>').join(''):'<p class="muted">No external source was needed.</p>';
}
function renderMeta(r){
  const labels={emergency:'Emergency action',urgent:'Urgent assessment',routine:'Routine review',self_care:'Self-care guidance',information:'Information'};
  $('urgency-title').textContent=labels[r.urgency]||'Information';
  $('urgency-badge').className='urgency '+r.urgency;
  $('urgency-badge').textContent=r.urgency.toUpperCase();
  $('safety-note').textContent=r.safety_note;
  $('emergency').classList.toggle('hidden',r.urgency!=='emergency');
  renderMedication(r.medication);
  renderSources(r.sources);
}
async function send(text){
  addMessage('user','<p>'+esc(text)+'</p>');
  $('message').value='';
  const loading=document.createElement('div');
  loading.className='message assistant';
  loading.innerHTML='<span class="avatar">MC</span><div class="bubble">Checking guidance…</div>';
  $('messages').appendChild(loading);
  try{
    const res=await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:text,context:{age_group:'unknown',medicines:[]}})});
    const body=await res.json();
    if(!res.ok) throw new Error(body.detail||'Request failed');
    loading.remove();
    const actions=body.actions?.length?'<div class="actions"><b>Next steps</b>'+body.actions.map(x=>'<span>'+esc(x)+'</span>').join('')+'</div>':'';
    addMessage('assistant',formatReply(body.reply)+actions+'<small>'+esc(body.safety_note)+'</small>');
    renderMeta(body);
  }catch(err){
    loading.remove();
    addMessage('assistant','<p>I could not complete that request.</p><small>'+esc(err.message)+'</small>');
  }
}
$('chat-form').addEventListener('submit',e=>{e.preventDefault();const text=$('message').value.trim();if(text)send(text)});
document.querySelectorAll('.prompt').forEach(btn=>btn.addEventListener('click',()=>send(btn.dataset.prompt)));