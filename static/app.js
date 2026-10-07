document.addEventListener('DOMContentLoaded',()=>{
 const button=document.querySelector('#match-button');
 if(!button)return;
 button.addEventListener('click',async()=>{
  const select=document.querySelector('#match-skills');
  const out=document.querySelector('#match-results');
  const ids=[...select.selectedOptions].map(o=>o.value);
  if(!ids.length){out.innerHTML='<p class="inline-error">Choose one or more skills to see matches.</p>';return}
  button.disabled=true;button.innerHTML='<span class="spinner-border spinner-border-sm"></span> Finding matches…';out.innerHTML='';
  try{
   const response=await fetch('/api/freelancers/match',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({skills:ids})});
   const data=await response.json();
   if(!data.results?.length){out.innerHTML='<div class="match-empty">No freelancers match those skills yet. Try a different combination.</div>';return}
   out.innerHTML=data.results.map(p=>`<article class="match-result"><div class="match-result-top"><div><strong>${escapeHtml(p.name)}</strong><small>${escapeHtml(p.title)}</small></div><span class="match-pill">${p.match}% match</span></div><div class="skill-row">${p.skills.filter(s=>ids.includes(String(s.id))).map(s=>`<span class="skill-chip ${s.verified?'checked':''}">${escapeHtml(s.name)} ${s.verified?'<i class="bi bi-patch-check-fill" title="Verified"></i>':''}</span>`).join('')}</div><small>${p.matched}/${ids.length} skills matched · ${p.verified_count} verified · ₹${p.hourly_rate}/hr</small><div class="match-actions"><a class="btn btn-sm btn-outline-dark" href="/freelancer/${p.id}">View profile</a><a class="btn btn-sm btn-dark" href="/request/${p.id}">Request project</a></div></article>`).join('');
  }catch(e){out.innerHTML='<p class="inline-error">Could not load matches. Please try again.</p>'}
  finally{button.disabled=false;button.innerHTML='Find matches <i class="bi bi-arrow-right"></i>'}
 });
 function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
});
