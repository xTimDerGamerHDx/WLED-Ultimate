#pragma once

static const char WLED_ULTIMATE_AUDIO_CONTROLS_V21_JS[] PROGMEM = R"V21AUDIO(
(()=>{
'use strict';
const page=document.getElementById('page-audio');
if(!page||document.getElementById('ultimateAudioControlsV21'))return;

const css=`
.audio-control-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:12px}.audio-control{border:1px solid var(--line);background:#07110e;border-radius:13px;padding:12px}.audio-control-head{display:flex;align-items:center;gap:8px;margin-bottom:8px}.audio-control-head b{font-size:11px}.audio-control-head span{margin-left:auto;color:var(--accent);font-size:11px;font-weight:800}.audio-control input[type=range]{width:100%;accent-color:var(--accent)}.audio-control select{width:100%;border:1px solid var(--line);background:#07100d;color:var(--text);border-radius:10px;padding:8px 9px}.sync-row{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:10px}.sync-btn{border:1px solid var(--line);background:#08130f;color:var(--muted);border-radius:10px;padding:9px 7px;cursor:pointer;font-size:10px}.sync-btn.active{background:var(--accent);border-color:var(--accent);color:#042016;font-weight:800}.audio-save-state{font-size:10px;color:var(--muted);margin-left:auto}.audio-save-state.ok{color:var(--accent)}.audio-save-state.bad{color:var(--danger)}
@media(max-width:620px){.audio-control-grid{grid-template-columns:1fr}}
`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

const card=document.createElement('div');
card.id='ultimateAudioControlsV21';card.className='section card';
card.innerHTML=`
<div style="display:flex;align-items:center;gap:8px"><div><h3 style="margin:0 0 3px">AudioReactive Control</h3><div class="sub">Direkte Laufzeitsteuerung des AudioReactive-Backends</div></div><div id="audioSaveState" class="audio-save-state">Lade…</div></div>
<div class="audio-control-grid">
 <div class="audio-control"><div class="audio-control-head"><b>Mic Gain</b><span id="audioGainV">60</span></div><input id="audioGain" type="range" min="0" max="255" step="1" value="60"><div class="sub">Manuelle Mikrofonverstärkung</div></div>
 <div class="audio-control"><div class="audio-control-head"><b>Noise Gate</b><span id="audioSquelchV">10</span></div><input id="audioSquelch" type="range" min="0" max="255" step="1" value="10"><div class="sub">Unterdrückt niedrige Störpegel</div></div>
 <div class="audio-control"><div class="audio-control-head"><b>Audio / FFT Sensitivity</b><span id="audioInputV">128</span></div><input id="audioInput" type="range" min="0" max="255" step="1" value="128"><div class="sub">Input-Level für Lautstärke und GEQ/FFT</div></div>
 <div class="audio-control"><div class="audio-control-head"><b>AGC</b></div><select id="audioAgc"><option value="0">Aus</option><option value="1">Normal</option><option value="2">Vivid</option><option value="3">Lazy</option></select><div class="sub" style="margin-top:7px">Automatische Pegelregelung</div></div>
 <div class="audio-control"><div class="audio-control-head"><b>FFT Scaling</b></div><select id="audioFftScale"><option value="0">Keine</option><option value="1">Logarithmisch</option><option value="2">Linear</option><option value="3">Square Root</option></select><div class="sub" style="margin-top:7px">Skalierung der 16 Frequenzbänder</div></div>
 <div class="audio-control"><div class="audio-control-head"><b>Audio Sync</b></div><div class="sync-row"><button class="sync-btn" data-sync="0">Aus</button><button class="sync-btn" data-sync="1">TX · Senden</button><button class="sync-btn" data-sync="2">RX · Empfangen</button></div><div class="sub" style="margin-top:7px">TX und RX sind WLED-kompatible Einzelmodi</div></div>
</div>`;
const notice=page.querySelector('.notice');if(notice)notice.before(card);else page.appendChild(card);

const $=id=>document.getElementById(id);
let currentSync=0,loading=false,saveTimer=0;
function setState(text,cls=''){const e=$('audioSaveState');if(!e)return;e.textContent=text;e.className='audio-save-state '+cls}
function paintSync(){document.querySelectorAll('#ultimateAudioControlsV21 [data-sync]').forEach(b=>b.classList.toggle('active',Number(b.dataset.sync)===currentSync))}
function bindRange(id,out){const e=$(id),v=$(out);if(!e||!v)return;e.oninput=()=>{v.textContent=e.value};e.onchange=scheduleSave}
function payload(){return new URLSearchParams({gain:$('audioGain').value,squelch:$('audioSquelch').value,input:$('audioInput').value,agc:$('audioAgc').value,fftScale:$('audioFftScale').value,sync:String(currentSync)})}
async function saveAudio(){if(loading)return;clearTimeout(saveTimer);setState('Speichere…');try{const r=await fetch('/ultimate/api/audio-config',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body:payload().toString()});if(!r.ok)throw Error(r.status);const j=await r.json();apply(j);setState('Gespeichert','ok');setTimeout(()=>setState('Live'),900)}catch(e){setState('Fehler','bad')}}
function scheduleSave(){if(loading)return;clearTimeout(saveTimer);saveTimer=setTimeout(saveAudio,220)}
function apply(j){loading=true;const map=[['audioGain','audioGainV','gain'],['audioSquelch','audioSquelchV','squelch'],['audioInput','audioInputV','input']];map.forEach(([id,out,k])=>{if(j[k]!==undefined){$(id).value=j[k];$(out).textContent=j[k]}});if(j.agc!==undefined)$('audioAgc').value=j.agc;if(j.fftScale!==undefined)$('audioFftScale').value=j.fftScale;if(j.sync!==undefined)currentSync=Number(j.sync);paintSync();loading=false}
async function loadAudioControls(){setState('Lade…');try{const r=await fetch('/ultimate/api/audio-config',{cache:'no-store'});if(!r.ok)throw Error(r.status);const j=await r.json();if(j.available===false){setState('Nicht verfügbar','bad');card.querySelectorAll('input,select,button').forEach(e=>e.disabled=true);return}apply(j);setState('Live','ok')}catch(e){setState('Offline','bad')}}

bindRange('audioGain','audioGainV');bindRange('audioSquelch','audioSquelchV');bindRange('audioInput','audioInputV');
$('audioAgc').onchange=scheduleSave;$('audioFftScale').onchange=scheduleSave;
document.querySelectorAll('#ultimateAudioControlsV21 [data-sync]').forEach(b=>b.onclick=()=>{currentSync=Number(b.dataset.sync);paintSync();scheduleSave()});
loadAudioControls();
})();
)V21AUDIO";
