export function onRequestGet({env}) {
  return Response.json({flights:Boolean(env.SERPAPI_KEY),hotels:Boolean(env.SERPAPI_KEY),needsAccessToken:true,source:'SerpApi',scheduled:false},{headers:{'Cache-Control':'no-store'}});
}
