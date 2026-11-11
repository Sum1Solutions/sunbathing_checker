export const category = score => score >= 78 ? 'Excellent' : score >= 60 ? 'Good' : score >= 38 ? 'Mixed' : 'Poor';
const clamp = n => Math.max(0, Math.min(1,n));
export function hourScore(temp, cloud, wind, rain) {
  if (![temp, cloud, wind, rain].every(v => typeof v === 'number' && Number.isFinite(v))) return null;
  const warmth = clamp(1-Math.abs(temp-79)/24);
  const sun = clamp(1-cloud/100);
  const breeze = clamp(1-Math.max(0,wind-5)/18);
  const dry = clamp(1-rain/70);
  return Math.round(100*(.45*warmth+.35*sun+.20*breeze)*(.4+.6*dry)*(.4+.6*sun)*(.6+.4*warmth));
}
export function weatherDays(data) {
  const h=data.hourly; if (!h?.time) throw Error('Hourly forecast missing');
  const byDate=new Map();
  h.time.forEach((time,i)=> {
    const hour=Number(time.slice(11,13)); if(hour<11||hour>16) return;
    const values=[h.apparent_temperature?.[i],h.cloud_cover?.[i],h.wind_speed_10m?.[i],h.precipitation_probability?.[i]];
    const score=hourScore(...values); if(score===null) return;
    const date=time.slice(0,10); const a=byDate.get(date)||[];
    a.push({score,temp:values[0],cloud:values[1],wind:values[2],rain:values[3]}); byDate.set(date,a);
  });
  return [...byDate].filter(([,a])=>a.length===6).map(([date,a])=> {
    const avg=k=>a.reduce((s,x)=>s+x[k],0)/a.length;
    return {date,score:Math.round(avg('score')),category:category(avg('score')),hours:a.filter(x=>x.score>=60).length,temp:Math.round(avg('temp')),cloud:Math.round(avg('cloud')),wind:Math.round(avg('wind')),rain:Math.round(avg('rain'))};
  });
}
export function bestStay(days,nights,earliest) {
  let best=null;
  for(let i=0;i<days.length-nights;i++) {
    const stay=days.slice(i,i+nights+1); if(stay[0].date<earliest) continue;
    if(stay.some((d,j)=>j&&Date.parse(d.date)-Date.parse(stay[j-1].date)!==86400000)) continue;
    // Arrival/departure days have less outdoor time; full days drive the rating.
    const full=stay.slice(1,-1); const useful=full.length?full:stay;
    const score=Math.round(useful.reduce((s,d)=>s+d.score,0)/useful.length);
    const candidate={start:stay[0].date,end:stay.at(-1).date,score,category:category(score),goodHours:useful.reduce((s,d)=>s+d.hours,0),days:stay};
    if(!best||score>best.score)best=candidate;
  }
  return best;
}
export async function forecast(dest,fetcher=fetch) {
  const u=new URL('https://api.open-meteo.com/v1/forecast');
  Object.entries({latitude:dest.lat,longitude:dest.lon,hourly:'apparent_temperature,cloud_cover,wind_speed_10m,precipitation_probability',temperature_unit:'fahrenheit',wind_speed_unit:'mph',timezone:'auto',forecast_days:14}).forEach(([k,v])=>u.searchParams.set(k,v));
  const r=await fetcher(u,{signal:AbortSignal.timeout(20000)}); if(!r.ok)throw Error(`Weather source returned ${r.status}`);
  return {days:weatherDays(await r.json()),observedAt:new Date().toISOString(),sourceUrl:u.href};
}
export function compareQuote(history,quote) {
  const matches=history.filter(q=>q.key===quote.key&&q.total>0&&q.observedAt!==quote.observedAt).sort((a,b)=>a.observedAt.localeCompare(b.observedAt));
  if(!matches.length)return {label:'First observation',drop:null,notify:false};
  const anchor=[...matches].reverse().find(q=>q.notified)||matches[0];
  const drop=anchor.total-quote.total, percent=drop/anchor.total*100;
  return {label:drop>0?`Down $${Math.round(drop)} (${Math.round(percent)}%)`:drop<0?`Up $${Math.round(-drop)} (${Math.round(-percent)}%)`:'No price change',drop,percent,notify:drop>=150&&percent>=10&&['Good','Excellent'].includes(quote.weatherCategory)&&quote.complete};
}
export function quoteKey(q) {return JSON.stringify([q.origin,q.destination,q.start,q.end,q.adults,q.hotelIdentity,q.rateTerms,q.flightIdentity]);}

export async function seasonalContext(dest,fetcher=fetch) {
  const year=new Date().getFullYear()-1;
  const u=new URL('https://archive-api.open-meteo.com/v1/archive');
  Object.entries({latitude:dest.lat,longitude:dest.lon,start_date:`${year-2}-01-01`,end_date:`${year}-12-31`,hourly:'apparent_temperature,cloud_cover,wind_speed_10m,precipitation',temperature_unit:'fahrenheit',wind_speed_unit:'mph',timezone:'auto'}).forEach(([k,v])=>u.searchParams.set(k,v));
  const r=await fetcher(u,{signal:AbortSignal.timeout(45000)});if(!r.ok)throw Error('Historical weather unavailable');
  const h=(await r.json()).hourly;if(!h?.time)throw Error('Historical hours unavailable');
  const months=Array.from({length:12},(_,i)=>({month:i+1,hours:0,good:0,temp:0}));
  h.time.forEach((t,i)=>{const hour=Number(t.slice(11,13));if(hour<11||hour>16)return;const rain=h.precipitation?.[i];if(typeof rain!=='number')return;const score=hourScore(h.apparent_temperature?.[i],h.cloud_cover?.[i],h.wind_speed_10m?.[i],rain>.1?100:0);if(score===null)return;const m=months[Number(t.slice(5,7))-1];m.hours++;m.good+=score>=60?1:0;m.temp+=h.apparent_temperature[i];});
  return {period:`${year-2}–${year}`,sourceUrl:u.href,months:months.filter(m=>m.hours).map(m=>({...m,goodPercent:Math.round(100*m.good/m.hours),temp:Math.round(m.temp/m.hours)}))};
}

export function windyWebcamsUrl(lat, lon) {
  const la = Number(lat).toFixed(4), lo = Number(lon).toFixed(4);
  return `https://www.windy.com/-Webcams/${la}/${lo}?${la},${lo},12`;
}

export function windyEmbedUrl(lat, lon) {
  const la = Number(lat).toFixed(4), lo = Number(lon).toFixed(4);
  return `https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=in&metricTemp=%C2%B0F&metricWind=mph&zoom=11&overlay=clouds&product=ecmwf&level=surface&lat=${la}&lon=${lo}&detailLat=${la}&detailLon=${lo}&marker=true`;
}

export function resolveCams(dest, selectedHotel = '') {
  const baseLat = Number(dest?.lat) || 26.1224;
  const baseLon = Number(dest?.lon) || -80.1373;
  const hasBeach = (dest?.hotels?.beach?.length > 0) || (dest?.cams || []).some(c => c.kind === 'beach' || c.kind === 'coast');
  const rawCams = Array.isArray(dest?.cams) && dest.cams.length > 0
    ? dest.cams
    : [{
        title: `${dest?.name || 'Destination'} ${hasBeach ? 'Coastline' : 'Sky & Resort'} View`,
        zone: 'City & resort area coordinates (backup)',
        kind: hasBeach ? 'beach' : 'sky',
        lat: baseLat,
        lon: baseLon,
        url: windyWebcamsUrl(baseLat, baseLon),
        isCoordinateBackup: true
      }];
  const needle = String(selectedHotel || '').trim().toLowerCase();
  const stopWords = new Set(['hotel', 'resort', 'beach', 'club', 'marriott', 'westin', 'ritz', 'carlton', 'ritz-carlton', 'four', 'seasons', 'spa', 'inn', 'grand', 'grande', 'house', 'palace', 'the']);
  const tokens = needle.split(/[^a-z0-9]+/).filter(w => w.length > 3 && !stopWords.has(w));
  const enriched = rawCams.map(cam => {
    const lat = Number.isFinite(Number(cam.lat)) ? Number(cam.lat) : baseLat;
    const lon = Number.isFinite(Number(cam.lon)) ? Number(cam.lon) : baseLon;
    const zoneText = String(cam.zone || '').toLowerCase();
    const exactMatch = Boolean(needle && zoneText.includes(needle));
    const tokenMatch = Boolean(!exactMatch && tokens.length && tokens.some(w => zoneText.includes(w)));
    const matchRank = exactMatch ? 2 : tokenMatch ? 1 : 0;
    return {
      ...cam,
      lat,
      lon,
      matchesSelectedHotel: matchRank > 0,
      matchRank,
      windyUrl: windyWebcamsUrl(lat, lon),
      embedUrl: windyEmbedUrl(lat, lon),
      searchBackupUrl: `https://www.google.com/search?q=${encodeURIComponent(`${cam.title} ${dest?.name || ''} ${dest?.state || ''} live webcam`.trim())}`
    };
  });
  return enriched.sort((a, b) => b.matchRank - a.matchRank);
}

export async function discoverOsmBackupCams(dest, cam, fetcher = fetch) {
  const lat = Number(cam?.lat ?? dest?.lat);
  const lon = Number(cam?.lon ?? dest?.lon);
  const fallbackLinks = [
    { label: 'Windy nearby webcams & daylight replay', url: windyWebcamsUrl(lat, lon) },
    { label: `EarthCam / public cams near ${dest?.name || 'destination'}`, url: `https://www.google.com/search?q=${encodeURIComponent(`${dest?.name || ''} ${dest?.state || ''} live beach sky webcam`.trim())}` },
    { label: 'OpenStreetMap area view', url: `https://www.openstreetmap.org/?mlat=${lat.toFixed(4)}&mlon=${lon.toFixed(4)}#map=13/${lat.toFixed(4)}/${lon.toFixed(4)}` }
  ];
  try {
    const query = `[out:json][timeout:8];(node["contact:webcam"](around:25000,${lat},${lon});node["man_made"="surveillance"]["surveillance:type"="camera"]["url"](around:25000,${lat},${lon});node["tourism"="viewpoint"]["url"](around:25000,${lat},${lon}););out body 5;`;
    const u = new URL('https://overpass-api.de/api/interpreter');
    u.searchParams.set('data', query);
    const r = await fetcher(u, { signal: AbortSignal.timeout(8500) });
    if (!r.ok) throw Error(`OSM backup status ${r.status}`);
    const data = await r.json();
    const items = (data?.elements || []).map(el => {
      const tags = el.tags || {};
      const url = tags['contact:webcam'] || tags.url || tags.website;
      if (!url || !/^https?:\/\//i.test(url)) return null;
      return {
        title: tags.name || tags.description || `Public OSM camera / viewpoint (${Number(el.lat).toFixed(3)}, ${Number(el.lon).toFixed(3)})`,
        url
      };
    }).filter(Boolean);
    return { items, fallbackLinks, status: items.length ? 'osm-found' : 'coordinate-backup' };
  } catch {
    return { items: [], fallbackLinks, status: 'coordinate-backup' };
  }
}
