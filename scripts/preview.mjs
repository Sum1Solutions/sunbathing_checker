import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const production='https://sunball-finder.pages.dev';
const publicFiles=new Set(['index.html','watch.html','watch-app.mjs','watch-core.mjs','watch-data.mjs']);
http.createServer(async(req,res)=>{
 const send=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(data));};
 try{
  const pathname=new URL(req.url,'http://localhost').pathname.replace(/\/+$/,'');
  if(pathname==='/api/watch-status')return send(200,{flights:true,hotels:false,source:'Existing production flight endpoint',scheduled:false});
  if(pathname==='/api/flights'&&req.method==='POST'){
   let text='';for await(const chunk of req){text+=chunk;if(text.length>10000)return send(413,{error:'Request too large'});}
   const r=await fetch(production+'/api/flights',{method:'POST',headers:{'Content-Type':'application/json'},body:text,signal:AbortSignal.timeout(40000)});
   const d=await r.json();return send(r.status,d);
  }
  if(pathname==='/api/watch-rates'&&req.method==='POST'){
   let text='';for await(const chunk of req){text+=chunk;if(text.length>10000)return send(413,{error:'Request too large'});}
   const input=JSON.parse(text);
   const r=await fetch(production+'/api/flights',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({origin:input.origin,destination:input.destination,departureDate:input.start,returnDate:input.end,adults:input.adults,nonStop:true}),signal:AbortSignal.timeout(40000)});
   const d=await r.json();if(!r.ok||!d.success)return send(r.status>=400?r.status:502,{error:d.error||'Existing flight source unavailable'});
   const offer=d.flights?.[0];
   return send(200,{observedAt:new Date().toISOString(),flight:offer?{price:offer.price,bothDirectionsVerified:false,outbound:{airline:offer.carrierName,flight_number:offer.flightNumber,departure_airport:{time:offer.departure?.time}},url:offer.bookingUrl}:null,hotel:null,complete:false,note:'Local preview reuses the existing production flight endpoint. New favorite-hotel and return-flight verification code requires deployment to use the production SerpApi secret.'});
  }
  const file=(!pathname||pathname==='')?'index.html':pathname.slice(1);
  if(!publicFiles.has(file)){res.writeHead(404);return res.end('Not found');}
  res.writeHead(200,{'Content-Type':file.endsWith('.html')?'text/html':'text/javascript'});res.end(await fs.readFile(path.join(root,file)));
 }catch{send(502,{error:'Connection failed; travel availability remains unknown.'});}
}).listen(8788,'127.0.0.1',()=>console.log('Sunball Preview: http://127.0.0.1:8788/ (index.html) and http://127.0.0.1:8788/watch.html'));
