import {destinations} from '../../watch-data.mjs';
const clean=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');
const finite=n=>typeof n==='number'&&Number.isFinite(n)&&n>0;
export async function onRequestPost({request,env}) {
  // The personal preview is local; hosted searches must not expose paid credits.
  if (!['localhost','127.0.0.1'].includes(new URL(request.url).hostname) &&
      (!env.WATCH_ACCESS_TOKEN || request.headers.get('X-Watch-Token') !== env.WATCH_ACCESS_TOKEN)) {
    return Response.json({error:'Personal watch access is required.'},{status:403});
  }
  if(!env.SERPAPI_KEY)return Response.json({error:'The SerpApi connection is not configured in this environment.',code:'provider_not_configured'},{status:503});
  try {
    const {origin,destination,start,end,adults=1,hotel}=await request.json();
    const d=destinations[destination];
    const names=d?Object.values(d.hotels).flat():[];
    if(!['PVD','BOS'].includes(origin)||!names.includes(hotel)||!Number.isInteger(adults)||adults<1||adults>4||!/^\d{4}-\d{2}-\d{2}$/.test(start)||!/^\d{4}-\d{2}-\d{2}$/.test(end)||!(Date.parse(end)>Date.parse(start)))return Response.json({error:'Invalid trip settings'},{status:400});
    // The preview runs locally. A hosted watch requires auth and a durable quota ledger.
    const search=async p=> {
      const url=new URL('https://serpapi.com/search.json');
      Object.entries({...p,api_key:env.SERPAPI_KEY,currency:'USD',gl:'us',hl:'en'}).forEach(([k,v])=>url.searchParams.set(k,v));
      const r=await fetch(url,{signal:AbortSignal.timeout(25000)});const data=await r.json();
      if(!r.ok||data.error)throw Error('Travel provider could not complete the search.');return data;
    };
    const params={engine:'google_flights',departure_id:origin,arrival_id:destination,outbound_date:start,return_date:end,type:1,stops:1,adults,travel_class:1,exclude_basic:true};
    const outbound=await search(params);
    const direct=(x,from,to)=>x.flights?.length===1&&!x.layovers?.length&&x.flights[0].departure_airport?.id===from&&x.flights[0].arrival_airport?.id===to;
    const offers=x=>[...(x.best_flights||[]),...(x.other_flights||[])].filter(x=>finite(x.price)).sort((a,b)=>a.price-b.price);
    const out=offers(outbound).find(x=>direct(x,origin,destination));
    let back=null;
    if(out?.departure_token){const returns=await search({...params,departure_token:out.departure_token});back=offers(returns).find(x=>direct(x,destination,origin));}
    const hotelData=await search({engine:'google_hotels',q:hotel+' '+d.name,check_in_date:start,check_out_date:end,adults});
    const properties=hotelData.properties||[];
    const exact=properties.find(p=>clean(p.name)===clean(hotel));
    const candidate=exact||properties.find(p=>clean(p.name).includes(clean(hotel))||clean(hotel).includes(clean(p.name)))||null;
    const total=candidate?.total_rate?.extracted_lowest;
    const inclusive=candidate?.total_rate?.extracted_before_taxes_fees;
    const flight=out?{outbound:out.flights[0],return:back?.flights[0]||null,price:back?.price||out.price,bothDirectionsVerified:Boolean(back),url:outbound.search_metadata?.google_flights_url||'https://www.google.com/travel/flights',priceInsights:outbound.price_insights||null}:null;
    return Response.json({observedAt:new Date().toISOString(),source:'SerpApi Google Flights / Hotels',requestsUsed:out?.departure_token?3:2,flight,hotel:candidate?{name:candidate.name,identityConfirmed:Boolean(exact),stayTotal:finite(total)?total:null,beforeTaxes:finite(inclusive)?inclusive:null,nightly:candidate.rate_per_night?.extracted_lowest||null,url:candidate.link||'https://www.google.com/travel/hotels',termsVerified:false}:null,complete:false,note:'Public hotel quote: room type, cancellation terms, and required fees still need direct verification.'},{headers:{'Cache-Control':'no-store'}});
  }catch{return Response.json({error:'Travel search failed; availability remains unknown.'},{status:502});}
}
