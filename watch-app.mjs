import {destinations} from './watch-data.mjs';
import {forecast,bestStay,compareQuote,quoteKey,seasonalContext,resolveCams,discoverOsmBackupCams} from './watch-core.mjs';
const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=n=>typeof n==='number'&&Number.isFinite(n)?new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n):'Unknown';
const safe=u=>{try{const x=new URL(u);return x.protocol==='https:'?x.href:'#';}catch{return '#';}};
const short=d=>new Date(d+'T12:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'});
let history=[];try{history=JSON.parse(localStorage.getItem('sunball-quotes-v1')||'[]');if(!Array.isArray(history))history=[];}catch{$('storage').textContent='Saved observations could not be read.';}
let used=0,connected=false,hotelConnected=false,results=[];
const tomorrow=new Date();tomorrow.setDate(tomorrow.getDate()+1);$('earliest').value=[tomorrow.getFullYear(),String(tomorrow.getMonth()+1).padStart(2,'0'),String(tomorrow.getDate()).padStart(2,'0')].join('-');$('earliest').min=$('earliest').value;
function usage(){$('used').textContent=`${used} / ${$('credits').value}`;}
function renderHistory(){$('history').innerHTML=history.length?'<ul>'+history.slice(-8).reverse().map(q=>`<li>${esc(q.hotelIdentity)} · ${short(q.start)}–${short(q.end)} · ${money(q.total)} <small>${esc(q.changeLabel)} · ${new Date(q.observedAt).toLocaleString()}</small></li>`).join('')+'</ul>':'No saved quotes yet.';}
renderHistory();$('credits').onchange=usage;
try{const r=await fetch('/api/watch-status');if(!r.ok)throw Error();const s=await r.json();connected=s.flights;hotelConnected=s.hotels;$('access').hidden=!s.needsAccessToken;$('connection').textContent=connected?(s.hotels?'Flights + hotels ready · prices on demand':'Existing flights connected · hotel lookup awaits deployment'):'Weather ready · travel key needed here';}catch{$('connection').textContent='Weather ready · travel connection not available here';}
$('scan').onclick=async()=> {
  if(!$('pvd').checked&&!$('bos').checked){$('message').textContent='Select at least one departure airport.';return;}
  $('scan').disabled=true;$('cards').replaceChildren();results=[];
  const adults=Number($('adults').value),nights=Number($('nights').value),earliest=$('earliest').value;
  const origins=[$('pvd').checked?'PVD':null,$('bos').checked?'BOS':null].filter(Boolean);
  let checked=0,failed=0;
  // Sequential, with a short pause: keep the public weather service below its minute limit.
  for(const [code,d] of Object.entries(destinations)){
    $('message').textContent=`Checking ${d.name}… ${checked+1} of 19. No travel-search credits used.`;
    try{const w=await forecast(d);const stay=bestStay(w.days,nights,earliest);if(stay)results.push({code,d,w,stay,adults,origins});else failed++;}catch{failed++;}
    checked++;$('checked').textContent=checked;await new Promise(resolve=>setTimeout(resolve,120));
  }
  results.sort((a,b)=>b.stay.score-a.stay.score);
  $('promising').textContent=results.filter(x=>x.stay.score>=60).length;
  $('message').textContent=`${results.length} destinations with usable trip forecasts. ${failed?`${failed} unavailable or outside your dates. `:''}Price only the ones that catch your eye. Schedule: not active.`;
  results.forEach((x,i)=>renderCard(x,i));$('scan').disabled=false;
};
function renderCard(x,i){
 const {code,d,w,stay,origins}=x;const names=[...new Set(Object.values(d.hotels).flat())];
 const hasCoast=(d.cams||[]).some(c=>c.kind==='beach'||c.kind==='coast');
 const camLabel=hasCoast?'🎥 Check live beach cams':'🎥 Check live sky & resort cams';
 const card=document.createElement('article');card.className='card';
 card.innerHTML=`<div class="card-top"><div><div class="eyebrow">${i<3?'Shortlist':'Also worth considering'} · ${esc(code)}</div><h3>${esc(d.name)}</h3></div><span class="badge ${stay.category}">${stay.category} for sunbathing</span></div><p>${short(stay.start)}–${short(stay.end)} · ${stay.goodHours} promising full-day outdoor hours<br><small>${Date.parse(stay.end)-Date.now()>7*86400000?"Extended forecast · lower confidence":"Near-term forecast"} · arrival/departure days excluded from rating</small></p><div class="days">${stay.days.map(day=>`<div class="day" title="${day.cloud}% cloud · ${day.wind} mph wind · ${day.rain}% rain chance"><small>${short(day.date)}</small><strong>${day.temp}° feels</strong>${day.category}<br>${day.wind} mph</div>`).join('')}</div><small>Observed ${new Date(w.observedAt).toLocaleTimeString()} · <a href="${safe(w.sourceUrl)}" target="_blank" rel="noopener">Forecast source</a> · comfort rating is provisional</small><label for="hotel-${i}">A hotel you like</label><select id="hotel-${i}">${names.map(n=>`<option>${esc(n)}</option>`).join('')}</select><label for="origin-${i}">Depart from</label><select id="origin-${i}">${origins.map(o=>`<option>${o}</option>`).join('')}</select><div class="actions"><button class="price-check" ${!connected?'disabled':''}>Check flights + hotel</button><a href="https://www.google.com/travel/hotels?q=${encodeURIComponent(d.name+' '+stay.start+' '+stay.end)}" target="_blank" rel="noopener">Browse hotel rates</a></div><div class="quote" hidden></div><div class="actions"><button class="secondary cam-toggle" type="button" aria-expanded="false">${camLabel}</button><button class="secondary season">Explore seasonal timing</button></div><div class="cam-result" hidden></div><div class="season-result" hidden></div><details class="quote-entry"><summary>Save a quote you verified directly</summary><label>Round-trip airfare for all travelers ($)<input type="number" class="manual-flight" min="1" step="0.01"></label><label>Hotel stay total including taxes and fees ($)<input type="number" class="manual-hotel" min="1" step="0.01"></label><label>Exact flights, room and cancellation terms<input class="manual-terms" placeholder="Flight numbers/times, room type, baggage, cancellation"></label><label class="check"><input type="checkbox" class="manual-confirm">I verified both nonstop directions and the hotel total/terms</label><button class="secondary manual-save">Save comparable quote</button><p class="manual-result" role="status"></p></details><div class="links"><a href="https://www.google.com/search?q=${encodeURIComponent(d.name+' official events calendar '+stay.start)}" target="_blank" rel="noopener">Events around these dates ↗</a><a href="https://www.google.com/search?q=${encodeURIComponent(d.name+' NOAA historical climate sunshine by month')}" target="_blank" rel="noopener">Seasonal context ↗</a></div>`;
 if(!hotelConnected)card.querySelector('.price-check').textContent='Check flights';
 const renderCamPanel=()=>{
   const camBox=card.querySelector('.cam-result');
   const selectedHotel=$('hotel-'+i)?.value||'';
   const cams=resolveCams(d,selectedHotel);
   const primary=cams[0];
   camBox.innerHTML=`<p><strong>Live hotel-zone cameras & sky check</strong> · <small>Zero search credits used. Verify coastal fog, wind, or sunshine near ${esc(selectedHotel||d.name)}.</small></p><div class="cam-grid">${cams.map((c,idx)=>`<div class="cam-item ${c.matchesSelectedHotel?'matched':''}"><strong>${c.kind==='beach'?'🏖️':c.kind==='coast'?'⚓':'☀️'} ${esc(c.title)}</strong><small>${esc(c.zone)}${c.matchesSelectedHotel?' · matches selected hotel':''}</small><div class="links"><a href="${safe(c.url)}" target="_blank" rel="noopener">Open live cam ↗</a><a href="${safe(c.windyUrl)}" target="_blank" rel="noopener">Daylight replay backup ↗</a><button type="button" class="secondary cam-focus" data-cam-index="${idx}" style="padding:4px 9px;font-size:12px">Focus sky map</button></div></div>`).join('')}</div><div class="cam-frame-wrap"><div class="cam-frame-head"><span class="cam-frame-label">Live sky, cloud & wind around <strong>${esc(primary.title)}</strong> (${primary.lat.toFixed(3)}, ${primary.lon.toFixed(3)})</span><a href="${safe(primary.searchBackupUrl)}" target="_blank" rel="noopener">Search backup feeds ↗</a></div><iframe class="cam-iframe" loading="lazy" referrerpolicy="no-referrer" sandbox="allow-scripts allow-same-origin allow-popups" title="Live sky and wind preview for ${esc(d.name)}" src="${safe(primary.embedUrl)}"></iframe></div><div class="actions"><button type="button" class="secondary cam-backup-btn" style="padding:7px 12px;font-size:12px">🔄 Check public OSM / coordinate backup cams</button></div><div class="cam-backup-status" style="margin-top:8px;font-size:12px"></div>`;
   camBox.querySelectorAll('.cam-focus').forEach(btn=>{
     btn.onclick=()=>{
       const chosen=cams[Number(btn.dataset.camIndex)]||primary;
       const iframe=camBox.querySelector('.cam-iframe');
       const label=camBox.querySelector('.cam-frame-label');
       if(iframe)iframe.src=safe(chosen.embedUrl);
       if(label)label.innerHTML=`Live sky, cloud & wind around <strong>${esc(chosen.title)}</strong> (${chosen.lat.toFixed(3)}, ${chosen.lon.toFixed(3)})`;
     };
   });
   const backupBtn=camBox.querySelector('.cam-backup-btn'),backupOut=camBox.querySelector('.cam-backup-status');
   backupBtn.onclick=async()=>{
     backupBtn.disabled=true;backupOut.textContent='Checking OpenStreetMap public camera nodes & coordinate backups…';
     const res=await discoverOsmBackupCams(d,primary);
     const osmHtml=res.items.length?`<p><strong>Public OSM camera/viewpoint nodes within 25 km:</strong></p><ul>${res.items.map(it=>`<li><a href="${safe(it.url)}" target="_blank" rel="noopener">${esc(it.title)} ↗</a></li>`).join('')}</ul>`:`<p class="muted">No direct stream URLs tagged in OpenStreetMap for this radius; using coordinate-verified webcam & daylight archives:</p>`;
     backupOut.innerHTML=osmHtml+`<div class="links">${res.fallbackLinks.map(lk=>`<a href="${safe(lk.url)}" target="_blank" rel="noopener">${esc(lk.label)} ↗</a>`).join('')}</div>`;
     backupBtn.disabled=false;
   };
 };
 const camBtn=card.querySelector('.cam-toggle'),camBox=card.querySelector('.cam-result');
 camBtn.onclick=()=>{
   camBox.hidden=!camBox.hidden;
   camBtn.setAttribute('aria-expanded',String(!camBox.hidden));
   camBtn.textContent=camBox.hidden?camLabel:(hasCoast?'🎥 Hide live beach cams':'🎥 Hide live sky & resort cams');
   if(!camBox.hidden&&!camBox.innerHTML)renderCamPanel();
 };
 card.querySelector(`#hotel-${i}`).onchange=()=>{if(!camBox.hidden)renderCamPanel();};
 card.querySelector('.price-check').onclick=async(e)=> {
   const btn=e.target,box=card.querySelector('.quote');
   if(used+3>Number($('credits').value)){box.hidden=false;box.textContent='Session search limit reached. Increase it only if you want more lookups.';return;}
   used+=3;usage();btn.disabled=true;btn.textContent='Checking this trip…';box.hidden=false;box.textContent=hotelConnected?'Checking nonstop directions and the selected hotel…':'Checking the existing flight source…';
   try{
     const settings={origin:$('origin-'+i).value,destination:code,start:stay.start,end:stay.end,adults:x.adults,hotel:$('hotel-'+i).value};
     const r=await fetch('/api/watch-rates',{method:'POST',headers:{'Content-Type':'application/json','X-Watch-Token':$('token').value},body:JSON.stringify(settings)});const data=await r.json();if(!r.ok)throw Error(data.error||'Travel source unavailable');
     const flight=data.flight,hotel=data.hotel,total=flight?.bothDirectionsVerified&&hotel?.stayTotal?flight.price+hotel.stayTotal:null;
     const q={...settings,observedAt:data.observedAt,total,hotelIdentity:hotel?.name||settings.hotel,rateTerms:'public quote; terms unverified',flightIdentity:JSON.stringify([flight?.outbound?.flight_number,flight?.outbound?.departure_airport?.time,flight?.return?.flight_number,flight?.return?.departure_airport?.time]),weatherCategory:stay.category,complete:false};q.key=quoteKey(q);
     const change=compareQuote(history,q);q.changeLabel=change.label;
     if(total){history.push(q);history=history.slice(-500);try{localStorage.setItem('sunball-quotes-v1',JSON.stringify(history));}catch{$('storage').textContent='Browser storage is full or unavailable; export to retain observations.';}renderHistory();}
     const leg=f=>f?`${f.airline||''} ${f.flight_number||''} · ${f.departure_airport?.time||'time unknown'}`:'Return direction not verified';
     box.innerHTML=`<div class="price">${total?money(total)+' combined quote':'Trip total incomplete'}</div><p>${esc(change.label)} · ${stay.category} weather</p><p>Flights: ${money(flight?.price)}${flight?.bothDirectionsVerified?' round trip':' · round-trip search quote; return unverified'} for ${x.adults} adult(s)<br><small>${esc(leg(flight?.outbound))}<br>${esc(leg(flight?.return))}</small></p><p>${esc(hotel?.name||(hotelConnected?'Selected hotel not found':'Hotel pricing not connected in this preview'))}<br>Hotel stay: ${money(hotel?.stayTotal)}${hotel&&!hotel.identityConfirmed?' · property match needs confirmation':''}</p><small>${esc(data.note)} This is a research candidate; alerts require verified comparable terms. Observed ${esc(new Date(data.observedAt).toLocaleString())}.</small><div class="links">${flight?`<a href="${safe(flight.url)}" target="_blank" rel="noopener">Review flights ↗</a>`:''}${hotel?`<a href="${safe(hotel.url)}" target="_blank" rel="noopener">Verify hotel & terms ↗</a>`:''}</div>`;
   }catch(err){box.textContent=err.message;box.classList.add('error');}
   finally{btn.disabled=false;btn.textContent=hotelConnected?'Refresh flights + hotel':'Refresh flights';}
 };
 card.querySelector('.season').onclick=async(e)=>{
   const btn=e.target,box=card.querySelector('.season-result');btn.disabled=true;box.hidden=false;box.textContent='Checking three years of historical weather…';
   try{const cacheKey='sunball-season-'+code+'-'+new Date().getFullYear();let context;try{context=JSON.parse(localStorage.getItem(cacheKey)||'null');}catch{}if(!context){context=await seasonalContext(d);try{localStorage.setItem(cacheKey,JSON.stringify(context));}catch{}}const best=[...context.months].sort((a,b)=>b.goodPercent-a.goodPercent).slice(0,3);
   box.innerHTML='<p><strong>Promising seasons · '+esc(context.period)+'</strong></p>'+best.map(m=>'<p>'+new Date(2000,m.month-1,1).toLocaleString('en-US',{month:'long'})+': '+m.goodPercent+'% of modeled 11am–4pm hours rated good/excellent · '+m.temp+'° average feels-like</p>').join('')+'<small>Historical modeled weather at city coordinates. Rain uses precipitation, not forecast probability. A seasonal lead, not a trip forecast. <a href="'+safe(context.sourceUrl)+'" target="_blank" rel="noopener">Source</a></small>';
   }catch(err){box.textContent=err.message;}finally{btn.disabled=false;}
 };
 card.querySelector('.manual-save').onclick=()=>{
  const message=card.querySelector('.manual-result'),air=Number(card.querySelector('.manual-flight').value),hotel=Number(card.querySelector('.manual-hotel').value),terms=card.querySelector('.manual-terms').value.trim();
  if(!(air>0&&hotel>0&&Number.isFinite(air+hotel))||!terms||!card.querySelector('.manual-confirm').checked){message.textContent='Enter both totals, exact terms, and confirm verification first.';return;}
  const q={origin:$('origin-'+i).value,destination:code,start:stay.start,end:stay.end,adults:x.adults,hotelIdentity:$('hotel-'+i).value,rateTerms:terms,flightIdentity:terms,total:air+hotel,weatherCategory:stay.category,complete:true,observedAt:new Date().toISOString(),source:'User-verified direct quote'};q.key=quoteKey(q);
  const change=compareQuote(history,q);q.changeLabel=change.label;q.notified=change.notify;history.push(q);history=history.slice(-500);
  try{localStorage.setItem('sunball-quotes-v1',JSON.stringify(history));message.textContent=(change.notify?'Worth a look: ':'Saved: ')+money(q.total)+' · '+change.label;}catch{message.textContent='Recorded in this session only; export to retain it.';}
  renderHistory();
 };$('cards').append(card);
}
$('export').onclick=()=>{const blob=new Blob([JSON.stringify({exportedAt:new Date().toISOString(),observations:history},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='sunball-observations.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
