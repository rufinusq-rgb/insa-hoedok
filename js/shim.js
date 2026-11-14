/* 회독 화면 코드가 쓰던 window.claude.use(...)를 이 앱에서 대신 제공한다.
   기록은 기기 안(IndexedDB)에 바로 저장되고, 몇 초 뒤 구글드라이브에 자동으로 올라간다. */
'use strict';
(function(){
const {Local, Drive, Sync, CFG} = window.INSA;
const BASE = new URL('./', location.href).href;

/* ---------- 드라이브 저장 상태 표시 + 자동 올리기 ---------- */
let dirty = false, timer = null, pushing = false, lastOk = 0, lastErr = '', shrink = null;
const pill = document.createElement('button');
pill.id = 'cloudPill'; pill.type = 'button';
pill.style.cssText = 'position:fixed;left:8px;bottom:calc(8px + env(safe-area-inset-bottom,0px));z-index:99999;font:12px/1.2 system-ui,sans-serif;' +
  'padding:5px 9px;border-radius:14px;border:1px solid #2e3440;background:#1c2028;color:#b4bbc8;box-shadow:0 2px 8px rgba(0,0,0,.4);opacity:.92';
function hhmm(t){ const d = new Date(t); return String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0'); }
function paint(){
  let txt, warn = false;
  if(!Drive.configured()){ txt = '☁ 기기에만 저장 중'; warn = true; }
  else if(pushing) txt = '☁ 드라이브에 저장 중…';
  else if(shrink){ txt = '⚠ ' + shrink.what + '로 줄어 저장 멈춤 · 눌러서 확인'; warn = true; }
  else if(!Drive.token() && (dirty || !lastOk)){ txt = '☁ 드라이브 연결하기 (눌러 주세요)'; warn = true; }
  else if(lastErr && dirty){ txt = '☁ 저장 못함 · 눌러서 다시'; warn = true; }
  else if(dirty) txt = '☁ 곧 드라이브에 저장';
  else if(lastOk) txt = '☁ 드라이브 저장됨 ' + hhmm(lastOk);
  else txt = '☁ 드라이브 연결됨';
  pill.textContent = txt;
  pill.style.borderColor = warn ? '#b8782a' : '#2e3440';
  pill.style.background = warn ? '#3a2a14' : '#1c2028';
  pill.style.color = warn ? '#f0c080' : '#b4bbc8';
}
async function push(opt){
  if(pushing || !Drive.configured()) { paint(); return; }
  if(!Drive.token()){ paint(); return; }
  pushing = true; paint();
  try{ await Sync.push(opt); dirty = false; lastOk = Date.now(); lastErr = ''; shrink = null; }
  catch(e){ lastErr = e.message || String(e); console.warn('drive push', e);
    if(e.code === 'conflict') alert(e.message);
    if(e.code === 'shrink'){ const first = !shrink; shrink = {prev: e.prev, now: e.now, what: e.what || ('빈칸 ' + e.prev + '→' + e.now + '개')}; if(first) alert(e.message + '\n\n왼쪽 아래 ⚠ 표시를 눌러 확인해 주세요.'); } }
  finally{ pushing = false; paint(); }
}
function schedule(){ dirty = true; paint(); clearTimeout(timer); timer = setTimeout(push, 5000); }
pill.addEventListener('click', async () => {
  if(shrink){
    if(confirm(shrink.what + '로 줄었습니다.\n\n직접 지운 게 맞으면 [확인] → 지금 상태를 드라이브에 저장합니다.\n모르는 사이에 줄었다면 [취소] → 드라이브는 줄기 전 상태로 둡니다. 그다음 클로드에게 알려 주세요.')){
      if(!Drive.token()){ try{ await Drive.connect(); }catch(e){ alert(e.message); return; } }
      await push({allowShrink: true});
    }
    return;
  }
  if(!Drive.configured()){ alert('아직 드라이브 연결 설정(클라이언트 ID)이 들어가지 않았습니다. 기록은 이 기기에 저장되고 있습니다.'); return; }
  if(!Drive.token()){ try{ await Drive.connect(); }catch(e){ alert(e.message); paint(); return; } }
  await push();
});
// 화면을 끄거나 다른 앱으로 넘어갈 때: 기다리던 저장을 바로 태블릿에 쓰고, 드라이브에도 올려 본다
document.addEventListener('visibilitychange', async () => {
  if(document.visibilityState !== 'hidden') return;
  try{ if(typeof Store !== 'undefined' && Store.q) await Promise.all(Object.keys(Store.q).filter(k => !k.startsWith('_t')).map(k => Store.flush(k))); }catch(e){}
  if(dirty) push();
});
window.addEventListener('pagehide', () => { try{ if(typeof Store !== 'undefined' && Store.q) Object.keys(Store.q).filter(k => !k.startsWith('_t')).forEach(k => Store.flush(k)); }catch(e){} if(dirty) push(); });
setInterval(() => { if(dirty && !pushing) push(); else paint(); }, 60000);
function mount(){ if(!document.body){ setTimeout(mount, 50); return; } document.body.appendChild(pill); paint(); }
mount();
Local.meta.get('pushedAt').then(t => { if(t){ lastOk = t; paint(); } });

/* ---------- db (claude db 흉내) ---------- */
function snapOf(path, rec){ return {id: path.split('/').pop(), exists: !!rec, data: () => rec ? JSON.parse(JSON.stringify(rec.v)) : undefined}; }
function docRef(path){
  return {
    path,
    async get(){ return snapOf(path, await Local.get(path)); },
    async set(val){ await Local.put(path, {v: JSON.parse(JSON.stringify(val)), t: Date.now()}); schedule(); },
    async delete(){ await Local.del(path); schedule(); },
    collection(name){ return colRef(path + '/' + name); }
  };
}
function colRef(path){
  return {
    path,
    doc(id){ return docRef(path + '/' + id); },
    async get(){
      const all = await Local.all(); const pre = path + '/'; const docs = [];
      for(const [k, rec] of Object.entries(all)) if(k.startsWith(pre) && !k.slice(pre.length).includes('/')) docs.push(snapOf(k, rec));
      return {docs, size: docs.length, empty: !docs.length};
    }
  };
}
const db = {doc: docRef, collection: colRef};
const user = {id: async () => 'me'};

/* ---------- downloads ---------- */
const downloads = {
  async save({filename, data}){
    const blob = data instanceof Blob ? data : new Blob([data], {type: /\.json$/i.test(filename) ? 'application/json' : 'application/octet-stream'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename;
    document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 4000);
    return {status:'saved'};
  }
};

/* ---------- assets (페이지 이미지 교체용) ---------- */
const assets = {
  async upload(blob, opt){
    const id = 'img-' + Date.now().toString(36) + Math.random().toString(36).slice(2,7);
    await Local.blob.put(id, blob);
    const c = await caches.open(CFG.CONTENT_CACHE);
    await c.put(BASE + '_blob/' + id, new Response(blob, {headers:{'Content-Type': (opt && opt.type) || blob.type || 'image/jpeg'}}));
    if(Drive.token()) Drive.saveBlob('이미지_' + id + '.jpg', blob, 'image/jpeg').catch(e => console.warn('img upload', e));
    return {id};
  }
};

const NS = {db, user, downloads, assets};
window.claude = {use: async (name) => NS[name] || null};
})();
