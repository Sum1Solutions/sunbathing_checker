import assert from 'node:assert/strict';
import {onRequestPost} from '../functions/api/watch-rates.js';
const request=data=>new Request('http://localhost/api/watch-rates',{method:'POST',body:JSON.stringify(data),headers:{'Content-Type':'application/json'}});
const input={origin:'BOS',destination:'FLL',start:'2026-10-10',end:'2026-10-14',adults:1,hotel:'W Fort Lauderdale'};
assert.equal((await onRequestPost({request:request(input),env:{}})).status,503);
assert.equal((await onRequestPost({request:new Request('https://public.example/api/watch-rates',{method:'POST',body:JSON.stringify(input)}),env:{SERPAPI_KEY:'test'}})).status,403,'public visitors cannot spend personal provider credits');
assert.equal((await onRequestPost({request:request({...input,hotel:'arbitrary query'}),env:{SERPAPI_KEY:'test'}})).status,400);
const old=globalThis.fetch;let calls=0;
globalThis.fetch=async url=>{
 calls++; const u=new URL(url);
 if(u.searchParams.get('engine')==='google_hotels')return Response.json({properties:[{name:'W Fort Lauderdale',total_rate:{extracted_lowest:1200},rate_per_night:{extracted_lowest:300},link:'https://example.com/hotel'}]});
 const back=u.searchParams.has('departure_token');
 return Response.json({best_flights:[{price:back?350:300,departure_token:back?undefined:'token',flights:[{airline:'Test Airline',departure_airport:{id:back?'FLL':'BOS'},arrival_airport:{id:back?'BOS':'FLL'}}]}]});
};
try{const r=await onRequestPost({request:request(input),env:{SERPAPI_KEY:'test'}});const d=await r.json();assert.equal(r.status,200);assert.equal(calls,3);assert.equal(d.flight.price,350);assert.equal(d.flight.bothDirectionsVerified,true);assert.equal(d.hotel.stayTotal,1200);assert.equal(d.complete,false,'public quote terms must not imply a verified alert');assert.equal(d.hotel.identityConfirmed,true);}finally{globalThis.fetch=old;}
console.log('Provider setup, allowed hotel validation, return direction, and unverified hotel terms checks passed.');
