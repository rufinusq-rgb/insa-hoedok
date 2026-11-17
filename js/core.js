/* 인사 회독 독립 앱 — 공통: 설정, 기기 안 저장(IndexedDB), 교재 묶음(Cache Storage), 구글드라이브 */
'use strict';
(function(){
const CFG = {
  // Google Cloud에서 받은 웹 클라이언트 ID. 공개해도 되는 값이다(비밀번호 아님).
  CLIENT_ID: '762064090079-16cnbffi2a62234cour2ukb622a7gvat.apps.googleusercontent.com',
  SCOPE: 'https://www.googleapis.com/auth/drive.file',
  FOLDER: '인사 회독 앱',
  // 편(회차) 목록. 새 편을 넣으면 여기에 덧붙인다. file = 드라이브에 올라갈 교재 묶음 이름
  ROUNDS: [
    {key:'r01', title:'제1편', file:'교재_r01.zip'},
    {key:'r02', title:'제2편', file:'교재_r02.zip'},
    {key:'r03', title:'제3편', file:'교재_r03.zip'},
    {key:'r04', title:'제4편', file:'교재_r04.zip'},
    {key:'r05', title:'제5편', file:'교재_r05.zip'}
  ],
  CONTENT_CACHE: 'insa-content-v1'
};

/* ---------- IndexedDB: 기록 (경로 → {v, t}) ---------- */
let _db = null;
function idb(){
  if(_db) return _db;
  _db = new Promise((ok, no) => {
    const r = indexedDB.open('insa-hoedok', 1);
    r.onupgradeneeded = () => { const d = r.result;
      if(!d.objectStoreNames.contains('docs')) d.createObjectStore('docs');
      if(!d.objectStoreNames.contains('meta')) d.createObjectStore('meta');
      if(!d.objectStoreNames.contains('blobs')) d.createObjectStore('blobs'); };
    r.onsuccess = () => ok(r.result);
    r.onerror = () => no(r.error);
  });
  return _db;
}
function tx(store, mode, fn){
  return idb().then(d => new Promise((ok, no) => {
    const t = d.transaction(store, mode), s = t.objectStore(store);
    let out; try{ out = fn(s); }catch(e){ no(e); return; }
    t.oncomplete = () => ok(out && 'result' in out ? out.result : out);
    t.onerror = () => no(t.error); t.onabort = () => no(t.error || new Error('abort'));
  }));
}
const Local = {
  get: (k) => tx('docs','readonly', s => s.get(k)),
  put: (k, v) => tx('docs','readwrite', s => s.put(v, k)),
  del: (k) => tx('docs','readwrite', s => s.delete(k)),
  all(){ return idb().then(d => new Promise((ok, no) => {
    const out = {}; const t = d.transaction('docs','readonly'); const c = t.objectStore('docs').openCursor();
    c.onsuccess = () => { const cur = c.result; if(cur){ out[cur.key] = cur.value; cur.continue(); } };
    t.oncomplete = () => ok(out); t.onerror = () => no(t.error);
  }));},
  async replaceAll(docs){
    const d = await idb();
    await new Promise((ok, no) => { const t = d.transaction('docs','readwrite'); const s = t.objectStore('docs');
      s.clear(); for(const [k,v] of Object.entries(docs)) s.put(v, k);
      t.oncomplete = ok; t.onerror = () => no(t.error); });
  },
  meta: {
    get: (k) => tx('meta','readonly', s => s.get(k)),
    put: (k, v) => tx('meta','readwrite', s => s.put(v, k))
  },
  blob: {
    get: (k) => tx('blobs','readonly', s => s.get(k)),
    put: (k, v) => tx('blobs','readwrite', s => s.put(v, k))
  }
};
/* 쪽 메모·펜 필기 합치기. L = 이 기기 기록, R = 드라이브 기록({v,t}). 드라이브 것과 다르면 새 기록, 같으면 null */
function mergeNote(L, R){
  const lv = (L && L.v) || {}, rv = (R && R.v) || null;
  if(!rv) return {v: lv, t: Date.now()};                     // 이 기기에만 있는 쪽
  const del = [...new Set([...(lv.mdel || []), ...(rv.mdel || [])])];
  const newerL = (L.t || 0) > (R.t || 0);
  const byId = new Map();
  for(const mm of (rv.memos || [])) if(mm && mm.id != null) byId.set(mm.id, mm);
  for(const mm of (lv.memos || [])){ if(!mm || mm.id == null) continue; if(!byId.has(mm.id) || newerL) byId.set(mm.id, mm); }
  const memos = [...byId.values()].filter(mm => !del.includes(mm.id));
  const useL = (lv.sT || 0) > (rv.sT || 0);
  const v = Object.assign({}, rv, {memos, mdel: del});
  if(useL){ v.strokes = lv.strokes || []; v.sT = lv.sT; v.sS = lv.sS; }
  if(JSON.stringify(v) === JSON.stringify(rv)) return null;
  return {v, t: Date.now()};
}
function lastWrite(docs){ let t = 0; for(const v of Object.values(docs)) if(v && v.t > t) t = v.t; return t; }

/* ---------- 교재 묶음: zip → Cache Storage ---------- */
const BASE = new URL('./', location.href).href;
const MIME = {jpg:'image/jpeg', jpeg:'image/jpeg', png:'image/png', webp:'image/webp', json:'application/json'};
const Content = {
  async has(rk){
    const c = await caches.open(CFG.CONTENT_CACHE);
    return !!(await c.match(BASE + 'data/' + rk + '.json')) && !!(await c.match(BASE + 'pages/' + rk + '/p00.jpg'));
  },
  async missing(){ const out = []; for(const r of CFG.ROUNDS) if(!(await Content.has(r.key))) out.push(r); return out; },
  // zip 안: data/rNN.json, data/rNN_words.json, pages/rNN/*.jpg, quiz/rNN/*.jpg (+ 선택: backup.json)
  async importZip(blob, onProg){
    const zip = await JSZip.loadAsync(blob);
    const names = Object.keys(zip.files).filter(n => !zip.files[n].dir);
    const rounds = new Set(); let backup = null;
    for(const n of names){ const m = n.match(/^data\/(r\d+)\.json$/); if(m) rounds.add(m[1]); }
    if(!rounds.size) throw new Error('교재 묶음이 아닙니다 (data/rNN.json 이 없습니다)');
    const c = await caches.open(CFG.CONTENT_CACHE);
    let i = 0;
    for(const n of names){
      i++;
      if(n === 'backup.json'){ backup = JSON.parse(await zip.files[n].async('string')); continue; }
      if(!/^(data|pages|quiz|_blob)\//.test(n)) continue;
      const ext = (n.split('.').pop() || '').toLowerCase();
      const buf = await zip.files[n].async('arraybuffer');
      if(n.startsWith('_blob/')) await Local.blob.put(n.slice(6), new Blob([buf], {type:'image/jpeg'}));
      await c.put(BASE + n, new Response(buf, {headers:{'Content-Type': MIME[ext] || 'application/octet-stream'}}));
      if(onProg && i % 10 === 0) onProg(i, names.length);
    }
    if(onProg) onProg(names.length, names.length);
    return {rounds:[...rounds], backup};
  },
  // 기기에 들어 있는 한 편을 다시 zip으로 묶는다(드라이브 보관용). 기록은 들어가지 않는다.
  async exportZip(rk){
    const c = await caches.open(CFG.CONTENT_CACHE); const zip = new JSZip(); let n = 0;
    for(const req of await c.keys()){
      if(!req.url.startsWith(BASE)) continue;
      const path = decodeURIComponent(req.url.slice(BASE.length));
      if(!(path === 'data/' + rk + '.json' || path === 'data/' + rk + '_words.json' || path.startsWith('pages/' + rk + '/') || path.startsWith('quiz/' + rk + '/'))) continue;
      const res = await c.match(req); if(!res) continue;
      zip.file(path, await res.arrayBuffer()); n++;
    }
    if(!n) throw new Error('기기에 이 편이 없습니다');
    return zip.generateAsync({type:'blob', compression:'STORE'});
  }
};

/* ---------- 구글드라이브 ---------- */
const TOK_KEY = 'insa:tok';
let _tokClient = null, _tokWait = null;
function loadGis(){
  if(window.google && google.accounts && google.accounts.oauth2) return Promise.resolve();
  return new Promise((ok, no) => { const s = document.createElement('script'); s.src = 'https://accounts.google.com/gsi/client';
    s.onload = ok; s.onerror = () => no(new Error('구글 로그인 도구를 불러오지 못했습니다(인터넷 확인)')); document.head.appendChild(s); });
}
const Drive = {
  configured(){ return !!CFG.CLIENT_ID; },
  token(){ try{ const t = JSON.parse(localStorage.getItem(TOK_KEY) || 'null'); if(t && t.exp > Date.now() + 60000) return t.tok; }catch(e){} return null; },
  // 반드시 사용자가 누른 직후에 부른다(팝업이 막히지 않게)
  async connect(){
    if(!CFG.CLIENT_ID) throw new Error('클라이언트 ID가 아직 설정되지 않았습니다');
    await loadGis();
    return new Promise((ok, no) => {
      _tokWait = {ok, no};
      if(!_tokClient) _tokClient = google.accounts.oauth2.initTokenClient({
        client_id: CFG.CLIENT_ID, scope: CFG.SCOPE,
        callback: (r) => { const w = _tokWait; _tokWait = null; if(!w) return;
          if(r.error){ w.no(new Error(r.error_description || r.error)); return; }
          localStorage.setItem(TOK_KEY, JSON.stringify({tok:r.access_token, exp: Date.now() + (r.expires_in||3600)*1000}));
          w.ok(r.access_token); },
        error_callback: (e) => { const w = _tokWait; _tokWait = null; if(w) w.no(new Error(e && e.type === 'popup_closed' ? '로그인 창이 닫혔습니다' : (e && e.message) || '로그인 실패')); }
      });
      _tokClient.requestAccessToken({prompt: localStorage.getItem('insa:consented') ? '' : 'consent'});
    }).then(t => { localStorage.setItem('insa:consented','1'); return t; });
  },
  async api(path, opt={}){
    const tok = Drive.token(); if(!tok){ const e = new Error('드라이브 연결이 필요합니다'); e.code = 'auth'; throw e; }
    const r = await fetch(path.startsWith('http') ? path : 'https://www.googleapis.com' + path,
      {...opt, headers:{...(opt.headers||{}), Authorization:'Bearer ' + tok}});
    if(r.status === 401){ localStorage.removeItem(TOK_KEY); const e = new Error('드라이브 연결이 만료되었습니다'); e.code = 'auth'; throw e; }
    if(!r.ok){ const e = new Error('드라이브 오류 ' + r.status + ': ' + (await r.text()).slice(0,200)); e.code = 'http'; throw e; }
    return r;
  },
  async folder(){
    const cached = localStorage.getItem('insa:folder'); if(cached) return cached;
    const q = encodeURIComponent("name='" + CFG.FOLDER + "' and mimeType='application/vnd.google-apps.folder' and trashed=false");
    const j = await (await Drive.api('/drive/v3/files?q=' + q + '&fields=files(id,name)&spaces=drive')).json();
    let id = j.files && j.files[0] && j.files[0].id;
    if(!id){ const r = await Drive.api('/drive/v3/files?fields=id', {method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({name: CFG.FOLDER, mimeType:'application/vnd.google-apps.folder'})}); id = (await r.json()).id; }
    localStorage.setItem('insa:folder', id); return id;
  },
  async find(name){
    const p = await Drive.folder();
    const q = encodeURIComponent("name='" + name.replace(/'/g,"\\'") + "' and '" + p + "' in parents and trashed=false");
    const j = await (await Drive.api('/drive/v3/files?q=' + q + '&fields=files(id,name,size,modifiedTime)&orderBy=modifiedTime desc')).json();
    return (j.files && j.files[0]) || null;
  },
  async list(){
    const p = await Drive.folder();
    const q = encodeURIComponent("'" + p + "' in parents and trashed=false");
    const j = await (await Drive.api('/drive/v3/files?q=' + q + '&fields=files(id,name,size,modifiedTime)&orderBy=name&pageSize=1000')).json();
    return j.files || [];
  },
  // 작은 파일(기록 JSON): 있으면 내용 교체, 없으면 새로 만든다
  async saveText(name, text, mime='application/json'){
    const f = await Drive.find(name);
    if(f){ await Drive.api('/upload/drive/v3/files/' + f.id + '?uploadType=media', {method:'PATCH', headers:{'Content-Type':mime}, body:text}); return f.id; }
    const p = await Drive.folder(); const bd = 'insa' + Math.random().toString(36).slice(2);
    const body = '--' + bd + '\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + JSON.stringify({name, parents:[p]}) +
      '\r\n--' + bd + '\r\nContent-Type: ' + mime + '\r\n\r\n' + text + '\r\n--' + bd + '--';
    const r = await Drive.api('/upload/drive/v3/files?uploadType=multipart&fields=id', {method:'POST', headers:{'Content-Type':'multipart/related; boundary=' + bd}, body});
    return (await r.json()).id;
  },
  // 큰 파일(교재 묶음 zip, 이미지)
  async saveBlob(name, blob, mime){
    const old = await Drive.find(name);
    const p = await Drive.folder();
    const init = await Drive.api(old ? '/upload/drive/v3/files/' + old.id + '?uploadType=resumable' : '/upload/drive/v3/files?uploadType=resumable',
      {method: old ? 'PATCH' : 'POST', headers:{'Content-Type':'application/json; charset=UTF-8', 'X-Upload-Content-Type': mime},
       body: JSON.stringify(old ? {} : {name, parents:[p]})});
    const loc = init.headers.get('Location');
    const r = await fetch(loc, {method:'PUT', headers:{'Content-Type':mime}, body:blob});
    if(!r.ok) throw new Error('올리기 실패 ' + r.status);
    return (await r.json()).id;
  },
  async readText(id){ return (await Drive.api('/drive/v3/files/' + id + '?alt=media')).text(); },
  async readBlob(id, onProg, total){
    const r = await Drive.api('/drive/v3/files/' + id + '?alt=media');
    if(!r.body || !onProg) return r.blob();
    const rd = r.body.getReader(); const parts = []; let got = 0;
    for(;;){ const {done, value} = await rd.read(); if(done) break; parts.push(value); got += value.length; onProg(got, total); }
    return new Blob(parts);
  }
};

/* ---------- 기록 ↔ 드라이브 ---------- */
function stamp(d){ d = d || new Date(); return d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0'); }
const Sync = {
  LATEST: '기록_최신.json',
  async snapshot(){ const docs = await Local.all(); return {app:'insa-hoedok', v:1, t: lastWrite(docs), saved: new Date().toISOString(), docs}; },
  // 사용자가 만든 빈칸 수(내 빈칸 + 직접 추가한 핵심 빈칸)
  count(docs){ const m = docs['data/users/me/r01']; const b = (m && m.v && m.v.add && m.v.add.blanks) || [];
    return b.filter(x => x.mine || x.core).length; },
  // 지켜보는 개수: 빈칸(내+핵심), 내가 만든 두문자, 메모
  counts(docs){ const m = docs['data/users/me/r01']; const a = (m && m.v && m.v.add) || {};
    let memo = 0; for(const [k, rec] of Object.entries(docs)) if(/\/notes\/p\d+$/.test(k) && rec && rec.v && Array.isArray(rec.v.memos)) memo += rec.v.memos.length;
    return {b: Sync.count(docs), d: (a.dumunja || []).filter(x => x.mine).length, m: memo}; },
  // 크게 줄었는지: 빈칸은 10개 넘게, 두문자·메모는 3개 넘게 줄고 90% 아래로 떨어지면
  shrunk(prev, now){ const L = [['b','빈칸',10],['d','두문자',3],['m','메모',3]]; const out = [];
    for(const [k, nm, lim] of L){ const p = prev && prev[k]; if(typeof p === 'number' && p - now[k] > lim && now[k] < p * 0.9) out.push({nm, prev: p, now: now[k]}); }
    return out; },
  async push(opt={}){
    const snap = await Sync.snapshot();
    if(!Object.keys(snap.docs).length) return null;
    // 안전장치: 빈칸이 갑자기 많이 줄었으면 드라이브 최신본을 덮어쓰지 않고 멈춘다
    const n = Sync.count(snap.docs); const cs = Sync.counts(snap.docs);
    let prevs = await Local.meta.get('pushedCounts');
    if(!prevs){ const pb = await Local.meta.get('pushedCount'); if(typeof pb === 'number') prevs = {b: pb}; }
    const sh = opt.allowShrink ? [] : Sync.shrunk(prevs, cs);
    if(sh.length){
      try{ await Drive.saveText('기록_확인필요_' + stamp() + '_' + Date.now() + '.json', JSON.stringify(snap)); }catch(e){}
      const what = sh.map(x => x.nm + ' ' + x.prev + '→' + x.now + '개').join(', ');
      const e = new Error(what + '로 갑자기 줄어서 드라이브 저장을 멈췄습니다. 드라이브의 기록은 줄기 전 상태 그대로입니다.');
      e.code = 'shrink'; e.what = what; e.prev = sh[0].prev; e.now = sh[0].now; throw e;
    }
    // 다른 기기가 그사이 드라이브에 더 새 기록을 올렸으면 덮어쓰지 않는다
    const cur = await Drive.find(Sync.LATEST);
    const pushedAt = (await Local.meta.get('pushedAt')) || 0;
    // (기기 시계가 드라이브 시계와 조금 달라도 놓치지 않게 2분 여유를 두고 읽어 본다)
    // 드라이브 기록이 이 기기가 마지막으로 올리거나 받은 것(pushedT)보다 새것이면, 이 기기가 아직 못 본 작업이 있다는 뜻 → 덮지 않는다
    if(cur && pushedAt && Date.parse(cur.modifiedTime) > pushedAt - 120000){
      const remote = JSON.parse(await Drive.readText(cur.id));
      const pushedT = (await Local.meta.get('pushedT')) || 0;
      if(remote && remote.t > pushedT && remote.t !== snap.t){
        await Drive.saveText('기록_충돌보관_' + stamp() + '_' + Date.now() + '.json', JSON.stringify(snap));
        const e = new Error('다른 기기에서 저장한 더 새 기록이 드라이브에 있습니다. 첫 화면에서 다시 열어 주세요. (이 기기 기록은 드라이브에 따로 보관했습니다)');
        e.code = 'conflict'; throw e;
      }
    }
    const text = JSON.stringify(snap);
    await Drive.saveText(Sync.LATEST, text);
    await Drive.saveText('기록_' + stamp() + '.json', text);
    // 시간대별 보관본(3시간 단위, 하루 최대 8개): 몇 시간 전 상태로도 되돌릴 수 있게
    const hr = new Date().getHours(); const slot = String(hr - hr % 3).padStart(2,'0');
    try{ await Drive.saveText('기록_' + stamp() + '_' + slot + '시.json', text); }catch(e){ console.warn('slot save', e); }
    await Local.meta.put('pushedT', snap.t);
    await Local.meta.put('pushedAt', Date.now());
    await Local.meta.put('pushedCount', n);
    await Local.meta.put('pushedCounts', cs);
    return snap.t;
  },
  // 앱을 열기 전에 한 번: 드라이브 쪽이 더 새것이면 받아 온다. 기기 쪽 기록은 버리지 않고 드라이브에 따로 남긴다.
  async pull(){
    const f = await Drive.find(Sync.LATEST);
    const local = await Local.all(); const lt = lastWrite(local);
    if(!f) return {action: Object.keys(local).length ? 'push' : 'none'};
    const remote = JSON.parse(await Drive.readText(f.id));
    if(!remote || remote.app !== 'insa-hoedok' || !remote.docs) return {action:'bad'};
    const pushedT = (await Local.meta.get('pushedT')) || 0;
    // 드라이브에 이 기기가 아직 못 본 작업이 없으면 기기 쪽을 올린다. (한 번도 주고받지 않은 기기는 예전처럼 시각 비교)
    if(pushedT ? remote.t <= pushedT : remote.t <= lt) return {action:'push'};
    if(Object.keys(local).length && lt > pushedT){                   // 양쪽 다 바뀜: 기기 쪽을 따로 보관
      await Drive.saveText('기록_충돌보관_' + stamp() + '_' + Date.now() + '.json', JSON.stringify({app:'insa-hoedok', v:1, t:lt, saved:new Date().toISOString(), docs:local}));
    }
    // 메모: 이 기기에서 바뀐 쪽 메모를 드라이브 쪽과 합친다(지운 메모는 mdel 묘비로 구별). 펜 필기: 더 나중에 고친 쪽(sT)을 남긴다.
    const docs = Object.assign({}, remote.docs); let merged = 0;
    for(const [k, L] of Object.entries(local)){
      if(!/\/notes\/p\d+$/.test(k) || !L || !(L.t > pushedT)) continue;     // 지난번 주고받은 뒤 이 기기에서 바뀐 쪽만
      const R = docs[k]; const m = mergeNote(L, R);
      if(m){ docs[k] = m; merged++; }
    }
    await Local.replaceAll(docs);
    await Local.meta.put('pushedCount', Sync.count(remote.docs));
    await Local.meta.put('pushedCounts', Sync.counts(remote.docs));
    await Local.meta.put('pushedT', remote.t);
    await Local.meta.put('pushedAt', Date.parse(f.modifiedTime) || Date.now());
    return {action:'pulled', t: remote.t, merged};
  }
};

window.INSA = {CFG, Local, Content, Drive, Sync, stamp, lastWrite, mergeNote};
window.INSA_ROUNDS = CFG.ROUNDS.map(r => r.key);
})();
