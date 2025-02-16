addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Forward the request to your Flask application
  const url = new URL(request.url)
  const response = await fetch(`https://your-flask-app.workers.dev${url.pathname}${url.search}`, request)
  return response
}
