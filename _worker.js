export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    url.protocol = "http:";
    url.host = "127.0.0.1:8080";
    
    return fetch(url, request);
  }
};
