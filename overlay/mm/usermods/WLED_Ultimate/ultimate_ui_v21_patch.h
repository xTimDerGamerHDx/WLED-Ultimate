#pragma once

static const char WLED_ULTIMATE_V21_JS[] PROGMEM = R"V21JS(
(()=>{
'use strict';
const css=`
.v21-toolbar{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}.v21-chip{border:1px solid var(--line);background:#08130f;color:#8eae9f;border-radius:999px;padding:7px 10px;font-size:10px;cursor:pointer}.v21-chip.active{color:#042016;background:var(--accent);border-color:var(--accent)}
.fx-card{position:relative;padding-right:39px}.fx-fav{position:absolute;right:7px;top:7px;width:28px;height:28px;border:1px solid var(--line);border-radius:9px;background:#07110e;color:#6e8f81;cursor:pointer;font-size:15px}.fx-fav.on{color:var(--warn);border-color:#6a5726}.fx-tag{display:inline-block;margin-top:5px;padding:2px 5px;border-radius:6px;background:#10251c;color:#74a18d;font-size:8px}
.audio-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:12px}.audio-metric{padding:10px;border:1px solid var(--line);border-radius:12px;background:#07110e}.audio-metric .k{font-size:9px;color:var(--muted);text-transform:uppercase}.audio-metric .v{font-size:18px;font-weight:800;margin-top:4px}.audio-viz.v21{height:145px}.audio-viz.v21 i{transition:height .12s linear}.peak-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#32483e;margin-right:5px}.peak-dot.on{background:var(--warn);box-shadow:0 0 14px #ffc857aa}.telemetry-status{display:flex;gap:8px;align-items:center;margin-top:9px;color:var(--muted);font-size:10px}
.health-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-top:12px}.health-chip{border:1px solid var(--line);border-radius:13px;background:#08130f;padding:11px}.health-chip .k{font-size:9px;color:var(--muted);text-transform:uppercase}.health-chip .v{font-size:13px;font-weight:800;margin-top:4px}.health-chip.good .v{color:var(--accent)}.health-chip.warn .v{color:var(--warn)}.health-chip.bad .v{color:var(--danger)}
.cap-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:7px;margin-top:10px}.cap{border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-size:10px;color:var(--muted)}.cap.on{color:var(--accent);border-color:#20563e}.cap.off{color:#68756f;opacity:.65}
@media(max-width:900px){.health-grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:620px){.audio-metrics{grid-template-columns:repeat(2,1fr)}.health-grid{grid-template-columns:repeat(2,1fr)}}`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

document.title='WLED Ultimate UI v2.1';
document.querySelectorAll('.brand span').forEach(e=>e.textContent='Modern UI v2.1 · Live');
document.querySelectorAll('.eyebrow').forEach(e=>{if(e.textContent.includes('WLED Ultimate'))e.textContent='WLED Ultimate UI v2.1'});
document.querySelectorAll('.legacy a').forEach(a=>{if(a.textContent.includes('Ultimate v1'))a.href='/ultimate-v1'});

let fxCategory='all';
const favKey='wledUltimateFxFavoritesV21';
function getFavs(){try{return new Set(JSON.parse(localStorage.getItem(favKey)||'[]').map(Number))}catch(e){return new Set()}}
function saveFavs(s){localStorage.setItem(favKey,JSON.stringify([...s]))}
function classifyFx(name=''){
 const n=String(name).toLowerCase();
 if(/audio|sound|music|freq|fft|geq|peak|spectrum/.test(n))return 'audio';
 if(/particle|spark|firework|starburst|meteor|grav|bounce|comet/.test(n))return 'particle';
 if(/2d|matrix|swirl|spaceship|crazy bees|game of life|black hole|frizzles/.test(n))return '2d';
 if(/solid|breathe|candle|aurora|ocean|lake|gradient|palette|sunrise|sunset/.test(n))return 'ambient';
 return 'dynamic';
}
const fxSearch=document.getElementById('effectSearch');
if(fxSearch&&!document.getElementById('v21FxToolbar')){
 fxSearch.insertAdjacentHTML('beforebegin','<div id="v21FxToolbar" class="v21-toolbar"><button class="v21-chip active" data-cat="all">Alle</button><button class="v21-chip" data-cat="fav">★ Favoriten</button><button class="v21-chip" data-cat="audio">Audio</button><button class="v21-chip" data-cat="particle">Particle</button><button class="v21-chip" data-cat="2d">2D/Matrix</button><button class="v21-chip" data-cat="ambient">Ambient</button><button class="v21-chip" data-cat="dynamic">Dynamic</button></div>');
 document.querySelectorAll('#v21FxToolbar [data-cat]').forEach(b=>b.onclick=()=>{fxCategory=b.dataset.cat;document.querySelectorAll('#v21FxToolbar [data-cat]').forEach(x=>x.classList.toggle('active',x===b));renderEffects()});
}
renderEffects=function(){
 const q=document.getElementById('effectSearch').value.toLowerCase(),s=seg(),box=document.getElementById('effectList'),favs=getFavs();box.innerHTML='';let shown=0;
 effects.forEach((n,i)=>{const cat=classifyFx(n);if(q&&!String(n).toLowerCase().includes(q))return;if(fxCategory==='fav'&&!favs.has(i))return;if(!['all','fav'].includes(fxCategory)&&cat!==fxCategory)return;shown++;
  const b=document.createElement('button');b.className='item fx-card'+(Number(s.fx)===i?' active':'');b.innerHTML=`<b>${n}</b><span>FX ${i}</span><em class="fx-tag">${cat}</em><button class="fx-fav ${favs.has(i)?'on':''}" title="Favorit">★</button>`;
  b.onclick=()=>sendSeg({fx:i});const star=b.querySelector('.fx-fav');star.onclick=e=>{e.stopPropagation();const f=getFavs();f.has(i)?f.delete(i):f.add(i);saveFavs(f);renderEffects()};box.appendChild(b)});
 setText('effectCount',shown+' / '+effects.length+' Effekte');if(!shown)box.innerHTML='<div class="empty">Keine Effekte für diesen Filter gefunden.</div>';
};

const audioCards=document.querySelectorAll('#page-audio .grid2 .card');
if(audioCards.length>1){audioCards[1].innerHTML='<h3>Live Audio Monitor</h3><div class="sub">Echte AudioReactive FFT-Telemetrie aus der Firmware</div><div class="audio-metrics"><div class="audio-metric"><div class="k">Level</div><div class="v" id="aLevel">--</div></div><div class="audio-metric"><div class="k">Bass</div><div class="v" id="aBass">--</div></div><div class="audio-metric"><div class="k">Mids</div><div class="v" id="aMids">--</div></div><div class="audio-metric"><div class="k">Treble</div><div class="v" id="aTreble">--</div></div></div><div id="audioViz" class="audio-viz v21"></div><div class="telemetry-status"><span id="aPeakDot" class="peak-dot"></span><span id="aPeak">Kein Peak</span><span>·</span><span id="aSource">Telemetrie wird geladen…</span></div><div class="stat-table" style="margin-top:8px"><div class="key">Audio Processing</div><div id="aProcessing" class="val">--</div><div class="key">UDP Sync</div><div id="aSync" class="val">--</div></div>'}
const audioNotice=document.querySelector('#page-audio .notice');if(audioNotice)audioNotice.textContent='UI v2.1 zeigt echte 16-Band-FFT-Werte des AudioReactive-Backends. Wenn AudioReactive in einem Build nicht verfügbar ist, wird das transparent als nicht verfügbar angezeigt.';
animateAudio=function(){};
function ensureBars(){const box=document.getElementById('audioViz');if(!box)return;if(box.children.length!==16){box.innerHTML='';for(let i=0;i<16;i++)box.appendChild(document.createElement('i'))}}
async function loadAudioTelemetry(){
 try{const r=await fetch('/ultimate/api/audio',{cache:'no-store'});if(!r.ok)throw Error(r.status);const a=await r.json();ensureBars();
  if(!a.available){setText('aSource','Audio-Telemetrie nicht verfügbar');[...document.querySelectorAll('#audioViz i')].forEach(x=>x.style.height='5%');return}
  setText('aLevel',Math.round(a.level??0));setText('aBass',Math.round(a.bass??0));setText('aMids',Math.round(a.mids??0));setText('aTreble',Math.round(a.treble??0));setText('aSource',a.source||'AudioReactive');setText('aProcessing',a.processing?'Aktiv':'Aus');
  const dot=document.getElementById('aPeakDot');if(dot)dot.classList.toggle('on',!!a.peak);setText('aPeak',a.peak?'PEAK':'Kein Peak');const bins=Array.isArray(a.fft)?a.fft:[];document.querySelectorAll('#audioViz i').forEach((x,i)=>{const v=Math.max(0,Math.min(255,Number(bins[i]||0)));x.style.height=(5+(v/255)*95)+'%'});
 }catch(e){setText('aSource','Telemetrie offline');}
}
setInterval(()=>{if(typeof activePage!=='undefined'&&activePage==='audio')loadAudioTelemetry()},250);setTimeout(loadAudioTelemetry,350);

const hw=document.getElementById('page-hardware');
if(hw&&!document.getElementById('v21Health'))hw.insertAdjacentHTML('beforeend','<div class="section card"><h3>Hardware Health</h3><div class="sub">Live-Bewertung aus WLED-Systemdaten und Ultimate-Capabilities</div><div id="v21Health" class="health-grid"></div></div><div class="section card"><h3>Build Capabilities</h3><div class="sub">Welche Ultimate-Funktionen diese Firmware tatsächlich bereitstellt</div><div id="v21Caps" class="cap-grid"></div></div>');
function healthClass(type,val){if(type==='wifi')return val>-67?'good':val>-78?'warn':'bad';if(type==='heap')return val>70000?'good':val>30000?'warn':'bad';return val?'good':'warn'}
function renderV21Hardware(){
 const u=state.ultimate||{},c=u.capabilities||{},rssi=Number(info.wifi?.rssi??-100),heap=Number(info.freeheap||0);const h=document.getElementById('v21Health');if(h)h.innerHTML=`<div class="health-chip ${healthClass('wifi',rssi)}"><div class="k">WiFi</div><div class="v">${rssi} dBm</div></div><div class="health-chip ${healthClass('heap',heap)}"><div class="k">Free Heap</div><div class="v">${bytes(heap)}</div></div><div class="health-chip ${healthClass('bool',c.psramAvailable??u.psramAvailable)}"><div class="k">PSRAM</div><div class="v">${(c.psramAvailable??u.psramAvailable)?'Bereit':'Nicht erkannt'}</div></div><div class="health-chip ${healthClass('bool',c.ethernetAvailable)}"><div class="k">Ethernet</div><div class="v">${c.ethernetAvailable?'Verfügbar':'Nicht im Build'}</div></div><div class="health-chip ${healthClass('bool',c.audioAvailable!==false)}"><div class="k">Audio</div><div class="v">${c.audioAvailable===false?'Nicht im Build':'Verfügbar'}</div></div>`;
 const caps=document.getElementById('v21Caps');if(caps){const labels={audioAvailable:'AudioReactive',particleAvailable:'Particle System',audioParticleAvailable:'Audio Particles',mmEffectsAvailable:'WLED-MM FX',ethernetAvailable:'Ethernet',wifiAvailable:'WiFi',performanceAvailable:'Performance Mode',psramAvailable:'PSRAM',experimentalAvailable:'Experimental FX'};caps.innerHTML='';Object.entries(labels).forEach(([k,n])=>{const on=c[k]!==false;const e=document.createElement('div');e.className='cap '+(on?'on':'off');e.textContent=(on?'✓ ':'– ')+n;caps.appendChild(e)})}
}
const oldRenderInfo=renderInfo;renderInfo=function(){oldRenderInfo();renderV21Hardware()};
const oldRenderState=renderState;renderState=function(){oldRenderState();renderV21Hardware()};
setTimeout(()=>{try{renderEffects();renderV21Hardware()}catch(e){}},500);
})();
)V21JS";
