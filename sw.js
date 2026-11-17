/* 오프라인용: 앱 파일은 새 버전을 먼저 시도하고 안 되면 저장본, 교재(쪽 이미지·데이터)는 기기에 넣어 둔 것에서 꺼낸다 */
const SHELL = 'insa-shell-v22';
const CONTENT = 'insa-content-v1';
const SHELL_FILES = ['./', 'index.html', 'app.html', 'js/core.js', 'js/shim.js', 'js/jszip.min.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });

function idbBlob(id){
  return new Promise(ok => {
    const r = indexedDB.open('insa-hoedok', 1);
    r.onerror = () => ok(null);
    r.onsuccess = () => { try{ const g = r.result.transaction('blobs','readonly').objectStore('blobs').get(id);
      g.onsuccess = () => ok(g.result || null); g.onerror = () => ok(null); }catch(err){ ok(null); } };
  });
}

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if(url.origin !== location.origin || e.request.method !== 'GET') return;
  const scope = new URL(self.registration.scope);
  const rel = url.pathname.slice(scope.pathname.length);
  if(/^(data|pages|quiz)\//.test(rel)){
    e.respondWith(caches.open(CONTENT).then(c => c.match(url.origin + url.pathname)).then(r => r || new Response('교재 파일이 기기에 없습니다: ' + rel, {status:404})));
    return;
  }
  if(/^_blob\//.test(rel)){
    e.respondWith(caches.open(CONTENT).then(c => c.match(url.origin + url.pathname)).then(async r => {
      if(r) return r;
      const b = await idbBlob(rel.slice(6));
      return b ? new Response(b, {headers:{'Content-Type':'image/jpeg'}}) : new Response('', {status:404});
    }));
    return;
  }
  // 앱 파일: 인터넷이 되면 새 버전, 안 되면 저장본
  e.respondWith(fetch(url.href, {cache:'no-cache', credentials:'same-origin'}).then(r => {
    if(r.ok){ const cp = r.clone(); caches.open(SHELL).then(c => c.put(e.request, cp)); }
    return r;
  }).catch(() => caches.match(e.request, {ignoreSearch:true}).then(r => r || caches.match('app.html'))));
});
