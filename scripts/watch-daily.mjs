// Free daily weather collection. Price queries remain explicitly opt-in.
import fs from 'node:fs/promises';
import path from 'node:path';
import {destinations} from '../watch-data.mjs';
import {forecast,bestStay} from '../watch-core.mjs';
const output=process.env.SUNBALL_DATA_DIR||path.join(process.env.HOME,'.local/share/sunball-finder');
const earliest=new Date(Date.now()+86400000).toISOString().slice(0,10);
const observations=[];
for(const [code,d] of Object.entries(destinations)){
 try{const w=await forecast(d);observations.push({code,destination:d.name,...w,stay:bestStay(w.days,4,earliest)});}catch(e){observations.push({code,destination:d.name,error:e.message});}
 await new Promise(r=>setTimeout(r,150));
}
const snapshot={checkedAt:new Date().toISOString(),scheduled:false,priceChecks:0,observations};
await fs.mkdir(output,{recursive:true});
await fs.writeFile(path.join(output,'latest.json'),JSON.stringify(snapshot,null,2));
await fs.appendFile(path.join(output,'weather-history.jsonl'),JSON.stringify(snapshot)+'\n');
console.log(JSON.stringify({checkedAt:snapshot.checkedAt,successful:observations.filter(o=>!o.error).length,shortlist:observations.filter(o=>o.stay?.score>=60).sort((a,b)=>b.stay.score-a.stay.score).slice(0,5).map(o=>({destination:o.destination,...o.stay})),savedTo:output,priceChecks:0},null,2));
process.exitCode=observations.every(o=>o.error)?1:0;
